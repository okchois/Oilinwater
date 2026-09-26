#ifndef OIW_BL_PORT_H
#define OIW_BL_PORT_H

#include <stdint.h>

/*
 * 부트로더 코어가 MCU 별 포트 계층에 요구하는 함수.
 * 주소는 MCU 의 절대 주소(예: 0x08008000). 반환값 0 = 성공.
 */

/* [addr, addr+len) 을 포함하는 모든 페이지 소거. addr/len 은 페이지 경계 정렬로 호출된다. */
int bl_flash_erase(uint32_t addr, uint32_t len);

/* 소거된 영역에 기록. addr 는 8 바이트 정렬, len 은 8 의 배수로 호출된다(마지막 블록은 0xFF 패딩). */
int bl_flash_write(uint32_t addr, const uint8_t *data, uint32_t len);

/* 메모리 맵드 읽기 포인터 (내장 플래시는 그대로 캐스팅). */
const uint8_t *bl_flash_ptr(uint32_t addr);

#endif
