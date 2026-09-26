/*
 * 호스트(PC) 시뮬레이션 포트: 부트로더 코어를 RAM 플래시로 실행한다.
 *
 * RS-485 대신 stdin/stdout 을 쓰며, 프레임 경계(실기에서는 3.5 문자 무신호)를
 * 2 바이트 리틀엔디언 길이 접두어로 표현한다. 응답이 없으면 길이 0 을 보낸다.
 *
 *   bl_host [--flash FILE] [--start-app]
 *     --flash FILE : 시작 시 슬롯 내용을 FILE 에서 읽고 종료 시 저장
 *     --start-app  : 앱 모드로 시작(레지스터 0x0000 = "AP"). 0x1000 에 0xB007 을 쓰면 부트로더 진입
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "bl_core.h"
#include "bl_port.h"
#include "crc.h"

#define SLOT_BASE  0x08008000u
#define SLOT_SIZE  0x18000u /* 96 KiB */
#define PAGE_SIZE  2048u
#define HW_ID      0x0001u
#define SLAVE_ADDR 1u

#define APP_ID          0x4150u /* "AP" */
#define APP_REG_BOOT    0x1000u
#define APP_BOOT_KEY    0xB007u

static uint8_t flash[SLOT_SIZE];

int bl_flash_erase(uint32_t addr, uint32_t len)
{
    if (addr < SLOT_BASE || addr + len > SLOT_BASE + SLOT_SIZE || addr % PAGE_SIZE || len % PAGE_SIZE)
        return -1;
    memset(flash + (addr - SLOT_BASE), 0xFF, len);
    return 0;
}

int bl_flash_write(uint32_t addr, const uint8_t *data, uint32_t len)
{
    if (addr < SLOT_BASE || addr + len > SLOT_BASE + SLOT_SIZE || addr % 8 || len % 8)
        return -1;
    uint8_t *dst = flash + (addr - SLOT_BASE);
    for (uint32_t i = 0; i < len; i++)
        if (dst[i] != 0xFF) /* NOR 플래시: 소거되지 않은 곳에 쓰기 금지 */
            return -1;
    memcpy(dst, data, len);
    return 0;
}

const uint8_t *bl_flash_ptr(uint32_t addr)
{
    static const uint8_t erased[8] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
    if (addr < SLOT_BASE || addr >= SLOT_BASE + SLOT_SIZE)
        return erased;
    return flash + (addr - SLOT_BASE);
}

static int read_frame(uint8_t *buf, size_t *len)
{
    uint8_t hdr[2];
    if (fread(hdr, 1, 2, stdin) != 2)
        return 0;
    *len = (size_t)(hdr[0] | (hdr[1] << 8));
    if (*len > BL_MAX_FRAME)
        return 0;
    return fread(buf, 1, *len, stdin) == *len;
}

static void write_frame(const uint8_t *buf, size_t len)
{
    uint8_t hdr[2] = {(uint8_t)len, (uint8_t)(len >> 8)};
    fwrite(hdr, 1, 2, stdout);
    fwrite(buf, 1, len, stdout);
    fflush(stdout);
}

static size_t add_crc(uint8_t *f, size_t n)
{
    uint16_t c = crc16_modbus(f, n);
    f[n] = (uint8_t)c;
    f[n + 1] = (uint8_t)(c >> 8);
    return n + 2;
}

/* 앱 모드 에뮬레이션: 모드 식별과 부트로더 진입 명령만 처리 */
static size_t app_handle(const uint8_t *q, size_t n, uint8_t *r, int *enter_boot)
{
    if (n < 8 || q[0] != SLAVE_ADDR || crc16_modbus(q, n - 2) != (uint16_t)(q[n - 2] | (q[n - 1] << 8)))
        return 0;
    uint16_t a = (uint16_t)(q[2] << 8 | q[3]), v = (uint16_t)(q[4] << 8 | q[5]);
    if (q[1] == 0x03 && a == 0 && v == 1) {
        uint8_t f[] = {SLAVE_ADDR, 0x03, 2, APP_ID >> 8, APP_ID & 0xFF, 0, 0};
        memcpy(r, f, 5);
        return add_crc(r, 5);
    }
    if (q[1] == 0x06 && a == APP_REG_BOOT && v == APP_BOOT_KEY) {
        *enter_boot = 1;
        memcpy(r, q, 6);
        return add_crc(r, 6);
    }
    r[0] = SLAVE_ADDR;
    r[1] = (uint8_t)(q[1] | 0x80);
    r[2] = 0x02;
    return add_crc(r, 3);
}

int main(int argc, char **argv)
{
    const char *flash_file = NULL;
    int app_mode = 0;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--flash") && i + 1 < argc)
            flash_file = argv[++i];
        else if (!strcmp(argv[i], "--start-app"))
            app_mode = 1;
    }

    memset(flash, 0xFF, sizeof flash);
    if (flash_file) {
        FILE *f = fopen(flash_file, "rb");
        if (f) {
            if (fread(flash, 1, sizeof flash, f) == 0)
                memset(flash, 0xFF, sizeof flash);
            fclose(f);
        }
    }

    bl_config_t cfg = {SLAVE_ADDR, HW_ID, SLOT_BASE, SLOT_SIZE};
    bl_init(&cfg);

    uint8_t req[BL_MAX_FRAME], resp[BL_MAX_FRAME];
    size_t len;
    int rc = 1;
    while (read_frame(req, &len)) {
        size_t n;
        if (app_mode) {
            int enter = 0;
            n = app_handle(req, len, resp, &enter);
            write_frame(resp, n);
            if (enter) {
                app_mode = 0; /* 실기: 플래그 저장 후 리셋 → 부트로더가 머묾 */
                bl_init(&cfg);
                fprintf(stderr, "sim: app -> bootloader\n");
            }
            continue;
        }
        n = bl_handle_frame(req, len, resp);
        write_frame(resp, n);
        if (bl_run_requested()) {
            uint32_t ver = 0;
            rc = bl_app_valid(&cfg, &ver) ? 0 : 1;
            fprintf(stderr, "sim: jump to app, version 0x%06X\n", (unsigned)ver);
            break;
        }
    }

    if (flash_file) {
        FILE *f = fopen(flash_file, "wb");
        if (f) {
            fwrite(flash, 1, sizeof flash, f);
            fclose(f);
        }
    }
    return rc;
}
