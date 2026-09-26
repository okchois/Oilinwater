#ifndef OIW_CRC_H
#define OIW_CRC_H

#include <stddef.h>
#include <stdint.h>

/* Modbus RTU CRC-16 (poly 0xA001 reflected, init 0xFFFF). 전송 시 하위 바이트 먼저. */
uint16_t crc16_modbus(const uint8_t *data, size_t len);

/* CRC-32 (IEEE 802.3, zlib.crc32 와 동일). crc 에 0 을 넣고 시작, 이어서 계산 가능. */
uint32_t crc32_update(uint32_t crc, const uint8_t *data, size_t len);

#endif
