#include "bl_core.h"

#include <string.h>

#include "bl_port.h"
#include "crc.h"
#include "fw_image.h"

/* Modbus 함수/예외 코드 */
#define FC_READ_HOLDING   0x03u
#define FC_WRITE_SINGLE   0x06u
#define FC_WRITE_MULTIPLE 0x10u
#define EX_ILLEGAL_FUNC   0x01u
#define EX_ILLEGAL_ADDR   0x02u
#define EX_ILLEGAL_VALUE  0x03u
#define EX_DEVICE_FAILURE 0x04u

#define DATA_REGS_MAX     (1u + BL_BLOCK_SIZE / 2u)

static struct {
    bl_config_t cfg;
    bl_state_t state;
    bl_error_t err;
    uint32_t total_size;
    uint32_t total_blocks;
    uint32_t next_block;
    int run_req;
    int app_valid;
    uint32_t app_version;
    uint8_t hdr_buf[FW_HDR_AREA]; /* 헤더 영역은 RAM 에 모았다가 FINISH 때 마지막으로 기록 */
} bl;

static uint16_t get_u16(const uint8_t *p) { return (uint16_t)((p[0] << 8) | p[1]); }

static void put_u16(uint8_t *p, uint16_t v)
{
    p[0] = (uint8_t)(v >> 8);
    p[1] = (uint8_t)v;
}

/* 헤더 검사. total_size != 0 이면 전송 중인 이미지 크기와도 대조. */
static bl_error_t check_header(const uint8_t *raw, uint32_t total_size)
{
    fw_header_t h;
    memcpy(&h, raw, sizeof h);
    if (h.magic != FW_HDR_MAGIC || h.hdr_version != FW_HDR_VERSION)
        return BL_ERR_HDR_INVALID;
    if (crc32_update(0, raw, offsetof(fw_header_t, hdr_crc32)) != h.hdr_crc32)
        return BL_ERR_HDR_INVALID;
    if (h.hw_id != bl.cfg.hw_id)
        return BL_ERR_HW_MISMATCH;
    if (h.load_addr != bl.cfg.slot_base + FW_HDR_AREA || h.payload_size == 0 ||
        h.payload_size > bl.cfg.slot_size - FW_HDR_AREA)
        return BL_ERR_HDR_INVALID;
    if (total_size != 0 && h.payload_size + FW_HDR_AREA != total_size)
        return BL_ERR_BAD_SIZE;
    return BL_ERR_NONE;
}

int bl_app_valid(const bl_config_t *cfg, uint32_t *fw_version)
{
    const uint8_t *raw = bl_flash_ptr(cfg->slot_base);
    fw_header_t h;
    bl_config_t saved = bl.cfg;

    bl.cfg = *cfg;
    bl_error_t e = check_header(raw, 0);
    bl.cfg = saved;
    if (e != BL_ERR_NONE)
        return 0;
    memcpy(&h, raw, sizeof h);
    if (crc32_update(0, bl_flash_ptr(h.load_addr), h.payload_size) != h.payload_crc32)
        return 0;
    if (fw_version)
        *fw_version = h.fw_version;
    return 1;
}

static void refresh_app_status(void)
{
    bl.app_valid = bl_app_valid(&bl.cfg, &bl.app_version);
    if (!bl.app_valid)
        bl.app_version = 0;
}

void bl_init(const bl_config_t *cfg)
{
    memset(&bl, 0, sizeof bl);
    bl.cfg = *cfg;
    bl.state = BL_STATE_IDLE;
    refresh_app_status();
}

int bl_run_requested(void) { return bl.run_req; }

static uint16_t read_reg(uint16_t addr)
{
    switch (addr) {
    case BL_REG_ID:         return BL_ID_BOOTLOADER;
    case BL_REG_BL_VERSION: return BL_VERSION;
    case BL_REG_HW_ID:      return bl.cfg.hw_id;
    case BL_REG_STATE:      return (uint16_t)bl.state;
    case BL_REG_ERROR:      return (uint16_t)bl.err;
    case BL_REG_BLOCK_SIZE: return BL_BLOCK_SIZE;
    case BL_REG_MAX_SIZE_H: return (uint16_t)(bl.cfg.slot_size >> 16);
    case BL_REG_MAX_SIZE_L: return (uint16_t)bl.cfg.slot_size;
    case BL_REG_NEXT_BLOCK: return (uint16_t)bl.next_block;
    case BL_REG_APP_VALID:  return (uint16_t)bl.app_valid;
    case BL_REG_APP_VER_H:  return (uint16_t)(bl.app_version >> 16);
    case BL_REG_APP_VER_L:  return (uint16_t)bl.app_version;
    default:                return 0;
    }
}

/* 명령 실행. 반환: 0 성공, 그 외 Modbus 예외 코드. */
static uint8_t fail(bl_error_t e, uint8_t ex, int fatal)
{
    bl.err = e;
    if (fatal)
        bl.state = BL_STATE_ERROR;
    return ex;
}

static uint8_t do_command(uint16_t cmd, uint32_t arg)
{
    switch (cmd) {
    case BL_CMD_BEGIN:
        if (arg <= FW_HDR_AREA || arg > bl.cfg.slot_size)
            return fail(BL_ERR_BAD_SIZE, EX_ILLEGAL_VALUE, 0);
        bl.app_valid = 0;
        bl.app_version = 0;
        if (bl_flash_erase(bl.cfg.slot_base, bl.cfg.slot_size) != 0)
            return fail(BL_ERR_FLASH_ERASE, EX_DEVICE_FAILURE, 1);
        memset(bl.hdr_buf, 0xFF, sizeof bl.hdr_buf);
        bl.total_size = arg;
        bl.total_blocks = (arg + BL_BLOCK_SIZE - 1u) / BL_BLOCK_SIZE;
        bl.next_block = 0;
        bl.state = BL_STATE_RECEIVING;
        bl.err = BL_ERR_NONE;
        return 0;

    case BL_CMD_FINISH: {
        if (bl.state != BL_STATE_RECEIVING)
            return fail(BL_ERR_BAD_STATE, EX_ILLEGAL_VALUE, 0);
        if (bl.next_block != bl.total_blocks)
            return fail(BL_ERR_INCOMPLETE, EX_ILLEGAL_VALUE, 0);
        fw_header_t h;
        memcpy(&h, bl.hdr_buf, sizeof h);
        if (crc32_update(0, bl_flash_ptr(h.load_addr), h.payload_size) != h.payload_crc32)
            return fail(BL_ERR_CRC_MISMATCH, EX_DEVICE_FAILURE, 1);
        /* 헤더를 마지막에 기록: 이 시점 이전에 전원이 꺼지면 앱은 무효로 남고 부트로더에 머문다. */
        if (bl_flash_write(bl.cfg.slot_base, bl.hdr_buf, FW_HDR_AREA) != 0)
            return fail(BL_ERR_FLASH_WRITE, EX_DEVICE_FAILURE, 1);
        refresh_app_status();
        if (!bl.app_valid)
            return fail(BL_ERR_CRC_MISMATCH, EX_DEVICE_FAILURE, 1);
        bl.state = BL_STATE_COMPLETE;
        bl.err = BL_ERR_NONE;
        return 0;
    }

    case BL_CMD_RUN:
        refresh_app_status();
        if (!bl.app_valid)
            return fail(BL_ERR_HDR_INVALID, EX_ILLEGAL_VALUE, 0);
        bl.run_req = 1;
        return 0;

    case BL_CMD_ABORT:
        bl.state = BL_STATE_IDLE;
        bl.err = BL_ERR_NONE;
        bl.next_block = 0;
        return 0;

    default:
        return fail(BL_ERR_BAD_STATE, EX_ILLEGAL_VALUE, 0);
    }
}

/* 데이터 블록: regs[0] = 블록 인덱스, regs[1..] = 데이터(레지스터 상위 바이트가 앞). */
static uint8_t do_data(const uint8_t *regs, uint16_t qty)
{
    if (bl.state != BL_STATE_RECEIVING)
        return fail(BL_ERR_BAD_STATE, EX_ILLEGAL_VALUE, 0);

    uint32_t idx = get_u16(regs);
    if (idx >= bl.total_blocks)
        return fail(BL_ERR_OUT_OF_ORDER, EX_ILLEGAL_VALUE, 0);

    uint32_t offset = idx * BL_BLOCK_SIZE;
    uint32_t n = bl.total_size - offset;
    if (n > BL_BLOCK_SIZE)
        n = BL_BLOCK_SIZE;
    if ((uint32_t)(qty - 1u) != (n + 1u) / 2u)
        return fail(BL_ERR_BAD_SIZE, EX_ILLEGAL_VALUE, 0);
    const uint8_t *data = regs + 2;

    /* 직전 블록 재전송(응답 유실 후 재시도): 내용이 같으면 성공 처리 */
    if (idx + 1u == bl.next_block) {
        const uint8_t *stored = offset < FW_HDR_AREA ? bl.hdr_buf + offset
                                                     : bl_flash_ptr(bl.cfg.slot_base + offset);
        if (memcmp(stored, data, n) != 0)
            return fail(BL_ERR_BLOCK_MISMATCH, EX_ILLEGAL_VALUE, 0);
        return 0;
    }
    if (idx != bl.next_block)
        return fail(BL_ERR_OUT_OF_ORDER, EX_ILLEGAL_VALUE, 0);

    if (offset < FW_HDR_AREA) {
        memcpy(bl.hdr_buf + offset, data, n);
        if (idx == 0) {
            /* 첫 블록에서 헤더를 조기 검증: 다른 보드용/손상 이미지는 바로 거부 */
            bl_error_t e = check_header(bl.hdr_buf, bl.total_size);
            if (e != BL_ERR_NONE)
                return fail(e, EX_ILLEGAL_VALUE, 1);
        }
    } else {
        uint8_t buf[BL_BLOCK_SIZE];
        uint32_t wlen = (n + 7u) & ~7u;
        memset(buf, 0xFF, sizeof buf);
        memcpy(buf, data, n);
        if (bl_flash_write(bl.cfg.slot_base + offset, buf, wlen) != 0)
            return fail(BL_ERR_FLASH_WRITE, EX_DEVICE_FAILURE, 1);
        if (memcmp(bl_flash_ptr(bl.cfg.slot_base + offset), data, n) != 0)
            return fail(BL_ERR_FLASH_WRITE, EX_DEVICE_FAILURE, 1);
    }
    bl.next_block++;
    return 0;
}

static size_t finish_frame(uint8_t *resp, size_t len)
{
    uint16_t crc = crc16_modbus(resp, len);
    resp[len++] = (uint8_t)crc;
    resp[len++] = (uint8_t)(crc >> 8);
    return len;
}

static size_t exception(uint8_t *resp, uint8_t fc, uint8_t ex)
{
    resp[0] = bl.cfg.slave_addr;
    resp[1] = (uint8_t)(fc | 0x80u);
    resp[2] = ex;
    return finish_frame(resp, 3);
}

size_t bl_handle_frame(const uint8_t *req, size_t len, uint8_t *resp)
{
    if (len < 4 || len > BL_MAX_FRAME)
        return 0;
    if (req[0] != bl.cfg.slave_addr)
        return 0; /* 브로드캐스트(0) 포함, 다른 주소는 무시 */
    if (crc16_modbus(req, len - 2) != (uint16_t)(req[len - 2] | (req[len - 1] << 8)))
        return 0;

    uint8_t fc = req[1];
    size_t pdu_len = len - 4; /* 주소, FC, CRC 제외 */
    const uint8_t *p = req + 2;

    switch (fc) {
    case FC_READ_HOLDING: {
        if (pdu_len != 4)
            return exception(resp, fc, EX_ILLEGAL_VALUE);
        uint16_t start = get_u16(p), qty = get_u16(p + 2);
        if (qty == 0 || qty > 125)
            return exception(resp, fc, EX_ILLEGAL_VALUE);
        if ((uint32_t)start + qty > BL_REG_INFO_COUNT)
            return exception(resp, fc, EX_ILLEGAL_ADDR);
        resp[0] = bl.cfg.slave_addr;
        resp[1] = fc;
        resp[2] = (uint8_t)(qty * 2u);
        for (uint16_t i = 0; i < qty; i++)
            put_u16(resp + 3 + 2 * i, read_reg((uint16_t)(start + i)));
        return finish_frame(resp, 3u + qty * 2u);
    }

    case FC_WRITE_SINGLE: {
        if (pdu_len != 4)
            return exception(resp, fc, EX_ILLEGAL_VALUE);
        if (get_u16(p) != BL_REG_CMD)
            return exception(resp, fc, EX_ILLEGAL_ADDR);
        uint16_t cmd = get_u16(p + 2);
        if (cmd == BL_CMD_BEGIN) /* BEGIN 은 크기 인자가 필요 → FC16 사용 */
            return exception(resp, fc, EX_ILLEGAL_VALUE);
        uint8_t ex = do_command(cmd, 0);
        if (ex)
            return exception(resp, fc, ex);
        memcpy(resp, req, 6); /* 요청 에코 */
        return finish_frame(resp, 6);
    }

    case FC_WRITE_MULTIPLE: {
        if (pdu_len < 5)
            return exception(resp, fc, EX_ILLEGAL_VALUE);
        uint16_t start = get_u16(p), qty = get_u16(p + 2);
        uint8_t bc = p[4];
        if (qty == 0 || qty > 123 || bc != qty * 2u || pdu_len != 5u + bc)
            return exception(resp, fc, EX_ILLEGAL_VALUE);
        const uint8_t *regs = p + 5;
        uint8_t ex;
        if (start == BL_REG_CMD && qty <= 3) {
            uint32_t arg = 0;
            if (qty == 3)
                arg = ((uint32_t)get_u16(regs + 2) << 16) | get_u16(regs + 4);
            else if (qty == 2)
                return exception(resp, fc, EX_ILLEGAL_VALUE);
            ex = do_command(get_u16(regs), arg);
        } else if (start == BL_REG_DATA && qty >= 2 && qty <= DATA_REGS_MAX) {
            ex = do_data(regs, qty);
        } else {
            return exception(resp, fc, EX_ILLEGAL_ADDR);
        }
        if (ex)
            return exception(resp, fc, ex);
        memcpy(resp, req, 6); /* 주소, FC, 시작, 수량 */
        return finish_frame(resp, 6);
    }

    default:
        return exception(resp, fc, EX_ILLEGAL_FUNC);
    }
}
