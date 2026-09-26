# 호스트 시뮬레이션 빌드 (MCU 빌드는 MCU 선정 후 별도 추가)
CC      ?= cc
CFLAGS  ?= -std=c11 -O2 -Wall -Wextra -Werror -pedantic
BUILD   := build

SRCS := common/crc.c bootloader/bl_core.c bootloader/port/host/main_host.c
INCS := -Icommon -Ibootloader

.PHONY: all clean
all: $(BUILD)/bl_host

$(BUILD)/bl_host: $(SRCS) common/*.h bootloader/*.h
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(INCS) -o $@ $(SRCS)

clean:
	rm -rf $(BUILD)
