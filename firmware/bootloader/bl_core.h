#ifndef OIW_BL_CORE_H
#define OIW_BL_CORE_H

#include <stddef.h>
#include <stdint.h>

/*
 * RS-485 Modbus RTU 부트로더 코어 (MCU 비의존).
 * 레지스터 맵과 절차는 docs/rs485-bootloader-design.md 참고.
 */

#define BL_VERSION          0x0100u  /* 1.0 */
#define BL_ID_BOOTLOADER    0x424Cu  /* "BL" : 레지스터 0x0000 */
#define BL_BLOCK_SIZE       128u     /* 데이터 블록 크기 [byte] */
#define BL_MAX_FRAME        256u     /* Modbus RTU ADU 최대 길이 */

/* 홀딩 레지스터 주소 */
#define BL_REG_ID           0x0000u
#define BL_REG_BL_VERSION   0x0001u
#define BL_REG_HW_ID        0x0002u
#define BL_REG_STATE        0x0003u
#define BL_REG_ERROR        0x0004u
#define BL_REG_BLOCK_SIZE   0x0005u
#define BL_REG_MAX_SIZE_H   0x0006u
#define BL_REG_MAX_SIZE_L   0x0007u
#define BL_REG_NEXT_BLOCK   0x0008u
#define BL_REG_APP_VALID    0x0009u
#define BL_REG_APP_VER_H    0x000Au
#define BL_REG_APP_VER_L    0x000Bu
#define BL_REG_INFO_COUNT   0x000Cu

#define BL_REG_CMD          0x0010u  /* CMD, ARG_H, ARG_L */
#define BL_REG_DATA         0x0100u  /* BLOCK_INDEX, DATA[0..63] */

/* 명령 */
#define BL_CMD_BEGIN        0x0001u  /* 인자: 전체 이미지 크기(헤더 포함) */
#define BL_CMD_FINISH       0x0002u
#define BL_CMD_RUN          0x0003u
#define BL_CMD_ABORT        0x0004u

typedef enum {
    BL_STATE_IDLE = 0,
    BL_STATE_RECEIVING = 1,
    BL_STATE_COMPLETE = 2,
    BL_STATE_ERROR = 3,
} bl_state_t;

typedef enum {
    BL_ERR_NONE = 0,
    BL_ERR_BAD_STATE = 1,
    BL_ERR_BAD_SIZE = 2,
    BL_ERR_OUT_OF_ORDER = 3,
    BL_ERR_FLASH_ERASE = 4,
    BL_ERR_FLASH_WRITE = 5,
    BL_ERR_HDR_INVALID = 6,
    BL_ERR_HW_MISMATCH = 7,
    BL_ERR_CRC_MISMATCH = 8,
    BL_ERR_INCOMPLETE = 9,
    BL_ERR_BLOCK_MISMATCH = 10,
} bl_error_t;

typedef struct {
    uint8_t  slave_addr;   /* 1..247 (설정 섹터에서 읽은 값, 앱과 동일) */
    uint16_t hw_id;
    uint32_t slot_base;    /* 앱 슬롯 시작 주소 (페이지 정렬) */
    uint32_t slot_size;    /* 앱 슬롯 크기 (헤더 영역 포함, 페이지 정렬) */
} bl_config_t;

void bl_init(const bl_config_t *cfg);

/*
 * 수신 프레임 1개(3.5 문자 무신호로 구분된 ADU, CRC 포함)를 처리하고 응답을 resp 에 쓴다.
 * 반환: 응답 길이. 0 이면 응답하지 않음(주소 불일치, 브로드캐스트, CRC 오류).
 */
size_t bl_handle_frame(const uint8_t *req, size_t len, uint8_t *resp);

/* RUN 명령 수신 후 true. 포트는 응답 송신 완료 뒤 앱 유효성 재확인 후 점프한다. */
int bl_run_requested(void);

/* 슬롯의 앱이 유효한가 (헤더 magic/CRC, hw_id, 페이로드 CRC). 유효하면 fw_version 반환. */
int bl_app_valid(const bl_config_t *cfg, uint32_t *fw_version);

#endif
