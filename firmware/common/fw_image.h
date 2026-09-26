#ifndef OIW_FW_IMAGE_H
#define OIW_FW_IMAGE_H

#include <stdint.h>

/*
 * 펌웨어 이미지 파일(.oiw) = [헤더 영역 FW_HDR_AREA 바이트] + [애플리케이션 바이너리]
 *
 * 앱 슬롯의 메모리 배치도 동일하다:
 *   slot_base                 : 헤더 (업데이트 마지막 단계에 기록 → 원자적 유효화)
 *   slot_base + FW_HDR_AREA   : 앱 벡터 테이블 (VTOR 정렬 512 B 충족)
 *
 * 모든 필드는 리틀엔디언.
 */

#define FW_HDR_AREA      512u
#define FW_HDR_MAGIC     0x4657494Fu /* "OIWF" */
#define FW_HDR_VERSION   1u

typedef struct {
    uint32_t magic;          /* FW_HDR_MAGIC */
    uint16_t hdr_version;    /* FW_HDR_VERSION */
    uint16_t hw_id;          /* 하드웨어 식별자: 다른 보드용 이미지 차단 */
    uint32_t fw_version;     /* 0x00MMmmpp (major.minor.patch) */
    uint32_t payload_size;   /* 앱 바이너리 크기 [byte] */
    uint32_t payload_crc32;  /* 앱 바이너리 CRC-32 */
    uint32_t load_addr;      /* 앱 시작 주소 = slot_base + FW_HDR_AREA */
    uint8_t  reserved[36];   /* 0 (향후 서명 등) */
    uint32_t hdr_crc32;      /* 위 60 바이트의 CRC-32 */
} fw_header_t;

_Static_assert(sizeof(fw_header_t) == 64, "fw_header_t must be 64 bytes");

#endif
