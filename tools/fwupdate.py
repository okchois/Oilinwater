"""RS-485(Modbus RTU) 펌웨어 업데이트 도구.

사용 예:
  # 1) 빌드된 앱 바이너리에 헤더를 붙여 이미지(.oiw) 생성
  python3 tools/fwupdate.py mkimage app.bin app.oiw --hw-id 1 --version 1.2.0

  # 2) 장치 정보 확인
  python3 tools/fwupdate.py info --port /dev/ttyUSB0 --addr 1

  # 3) 업데이트 (앱 실행 중이면 자동으로 부트로더 진입)
  python3 tools/fwupdate.py flash app.oiw --port /dev/ttyUSB0 --addr 1 --baud 19200 --parity E

시리얼 사용에는 pyserial 이 필요하다 (pip install pyserial).
테스트용으로 --sim "<명령>" 을 주면 호스트 시뮬레이터(firmware/build/bl_host)와 통신한다.
프로토콜: docs/rs485-bootloader-design.md
"""

import argparse
import shlex
import struct
import subprocess
import sys
import time
import zlib

# ---- 이미지 형식 (firmware/common/fw_image.h 와 일치해야 함) ----
HDR_AREA = 512
HDR_MAGIC = 0x4657494F  # "OIWF"
HDR_VERSION = 1
HDR_FMT = "<IHHIIII36s"  # hdr_crc32 제외 60 바이트
DEFAULT_SLOT_BASE = 0x08008000

# ---- 레지스터 맵 (firmware/bootloader/bl_core.h 와 일치해야 함) ----
ID_BOOTLOADER = 0x424C  # "BL"
ID_APP = 0x4150  # "AP"
REG_ID = 0x0000
REG_INFO_COUNT = 0x000C
REG_CMD = 0x0010
REG_DATA = 0x0100
APP_REG_BOOT = 0x1000
APP_BOOT_KEY = 0xB007
CMD_BEGIN, CMD_FINISH, CMD_RUN, CMD_ABORT = 1, 2, 3, 4

BL_ERRORS = {
    0: "none", 1: "bad state", 2: "bad size", 3: "out of order", 4: "flash erase",
    5: "flash write", 6: "header invalid", 7: "hw id mismatch", 8: "crc mismatch",
    9: "incomplete", 10: "block mismatch",
}


def crc16_modbus(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


def parse_version(s: str) -> int:
    major, minor, patch = (int(x) for x in s.split("."))
    if not all(0 <= x <= 255 for x in (major, minor, patch)):
        raise ValueError("version fields must be 0..255")
    return (major << 16) | (minor << 8) | patch


def fmt_version(v: int) -> str:
    return f"{(v >> 16) & 0xFF}.{(v >> 8) & 0xFF}.{v & 0xFF}"


def make_image(payload: bytes, hw_id: int, version: int, slot_base: int = DEFAULT_SLOT_BASE) -> bytes:
    head = struct.pack(HDR_FMT, HDR_MAGIC, HDR_VERSION, hw_id, version, len(payload),
                       zlib.crc32(payload), slot_base + HDR_AREA, bytes(36))
    head += struct.pack("<I", zlib.crc32(head))
    return head + b"\xFF" * (HDR_AREA - len(head)) + payload


def parse_image(image: bytes) -> dict:
    if len(image) <= HDR_AREA:
        raise ValueError("image too small")
    fields = struct.unpack_from(HDR_FMT, image)
    (hdr_crc,) = struct.unpack_from("<I", image, 60)
    magic, hver, hw_id, version, size, pcrc, load_addr, _ = fields
    if magic != HDR_MAGIC or hver != HDR_VERSION or zlib.crc32(image[:60]) != hdr_crc:
        raise ValueError("invalid image header")
    if size != len(image) - HDR_AREA or zlib.crc32(image[HDR_AREA:]) != pcrc:
        raise ValueError("payload size/CRC mismatch")
    return {"hw_id": hw_id, "version": version, "size": size, "load_addr": load_addr}


# ---- 전송 계층 ----
class TransportTimeout(Exception):
    pass


class SerialTransport:
    """RS-485 반이중. 자동 방향전환(USB-RS485 변환기) 가정."""

    def __init__(self, port, baud, parity, stopbits):
        try:
            import serial
        except ImportError:
            sys.exit("pyserial 이 필요합니다: pip install pyserial")
        self.ser = serial.Serial(port, baud, bytesize=8, parity=parity, stopbits=stopbits, timeout=0.05)

    def transact(self, frame: bytes, timeout: float) -> bytes:
        self.ser.reset_input_buffer()
        self.ser.write(frame)
        self.ser.flush()
        deadline = time.monotonic() + timeout

        def read(n):
            buf = b""
            while len(buf) < n:
                if time.monotonic() > deadline:
                    raise TransportTimeout()
                buf += self.ser.read(n - len(buf))
            return buf

        # 응답 길이를 함수 코드로 결정 (무신호 타이밍에 의존하지 않음)
        head = read(2)
        if head[1] & 0x80:
            return head + read(3)
        if head[1] == 0x03:
            bc = read(1)
            return head + bc + read(bc[0] + 2)
        return head + read(6)


class PipeTransport:
    """호스트 시뮬레이터용: 2 바이트 LE 길이 접두 프레임."""

    def __init__(self, cmd):
        self.proc = subprocess.Popen(shlex.split(cmd), stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def transact(self, frame: bytes, timeout: float) -> bytes:
        self.proc.stdin.write(struct.pack("<H", len(frame)) + frame)
        self.proc.stdin.flush()
        hdr = self.proc.stdout.read(2)
        if len(hdr) < 2:
            raise TransportTimeout()
        (n,) = struct.unpack("<H", hdr)
        if n == 0:
            raise TransportTimeout()
        return self.proc.stdout.read(n)

    def close(self):
        self.proc.stdin.close()
        rc = self.proc.wait(timeout=10)
        self.proc.stdout.close()
        return rc


# ---- Modbus RTU 마스터 ----
class ModbusError(Exception):
    def __init__(self, code):
        super().__init__(f"Modbus exception 0x{code:02X}")
        self.code = code


class ModbusClient:
    def __init__(self, transport, addr, timeout=1.0, retries=3):
        self.t, self.addr, self.timeout, self.retries = transport, addr, timeout, retries

    def _request(self, pdu: bytes, timeout=None) -> bytes:
        frame = bytes([self.addr]) + pdu
        frame += struct.pack("<H", crc16_modbus(frame))
        last = None
        for _ in range(self.retries + 1):
            try:
                resp = self.t.transact(frame, timeout or self.timeout)
            except TransportTimeout as e:
                last = e
                continue
            if len(resp) < 4 or crc16_modbus(resp[:-2]) != struct.unpack("<H", resp[-2:])[0] or resp[0] != self.addr:
                last = TransportTimeout("bad response")
                continue
            if resp[1] & 0x80:
                raise ModbusError(resp[2])
            return resp[1:-2]
        raise TimeoutError(f"no valid response ({last})")

    def read_holding(self, start, qty):
        pdu = self._request(struct.pack(">BHH", 0x03, start, qty))
        return list(struct.unpack(f">{qty}H", pdu[2:2 + 2 * qty]))

    def write_single(self, reg, value, timeout=None):
        self._request(struct.pack(">BHH", 0x06, reg, value), timeout)

    def write_multiple(self, start, values, timeout=None):
        body = struct.pack(f">BHHB{len(values)}H", 0x10, start, len(values), 2 * len(values), *values)
        self._request(body, timeout)


# ---- 업데이트 절차 ----
def read_info(mb: ModbusClient) -> dict:
    r = mb.read_holding(REG_ID, REG_INFO_COUNT)
    return {
        "id": r[0], "bl_version": r[1], "hw_id": r[2], "state": r[3], "error": r[4],
        "block_size": r[5], "max_size": (r[6] << 16) | r[7], "next_block": r[8],
        "app_valid": r[9], "app_version": (r[10] << 16) | r[11],
    }


def enter_bootloader(mb: ModbusClient, wait=5.0, log=print):
    mode = mb.read_holding(REG_ID, 1)[0]
    if mode == ID_BOOTLOADER:
        return
    if mode != ID_APP:
        raise RuntimeError(f"unknown device id 0x{mode:04X}")
    log("앱 실행 중 → 부트로더 진입 요청")
    mb.write_single(APP_REG_BOOT, APP_BOOT_KEY)
    deadline = time.monotonic() + wait
    while time.monotonic() < deadline:
        try:
            if mb.read_holding(REG_ID, 1)[0] == ID_BOOTLOADER:
                return
        except (TimeoutError, ModbusError):
            pass
        time.sleep(0.2)
    raise RuntimeError("부트로더 진입 실패")


def flash(mb: ModbusClient, image: bytes, run=True, log=print):
    meta = parse_image(image)
    enter_bootloader(mb, log=log)
    info = read_info(mb)
    if info["hw_id"] != meta["hw_id"]:
        raise RuntimeError(f"HW ID 불일치: 장치 {info['hw_id']}, 이미지 {meta['hw_id']}")
    if len(image) > info["max_size"]:
        raise RuntimeError("이미지가 슬롯보다 큼")
    bs = info["block_size"]
    blocks = (len(image) + bs - 1) // bs

    def bl_error(e):
        err = mb.read_holding(0x0004, 1)[0]
        return RuntimeError(f"{e}: bootloader error {err} ({BL_ERRORS.get(err, '?')})")

    log(f"이미지 v{fmt_version(meta['version'])}, {len(image)} B, {blocks} 블록 전송")
    try:
        mb.write_multiple(REG_CMD, [CMD_BEGIN, len(image) >> 16, len(image) & 0xFFFF], timeout=10.0)
        t0 = time.monotonic()
        for i in range(blocks):
            chunk = image[i * bs:(i + 1) * bs]
            if len(chunk) % 2:
                chunk += b"\xFF"
            mb.write_multiple(REG_DATA, [i] + list(struct.unpack(f">{len(chunk) // 2}H", chunk)))
            if i % 64 == 0 or i == blocks - 1:
                log(f"  {i + 1}/{blocks} ({100 * (i + 1) // blocks}%)")
        mb.write_single(REG_CMD, CMD_FINISH, timeout=5.0)
    except ModbusError as e:
        raise bl_error(e) from e
    log(f"전송 및 검증 완료 ({time.monotonic() - t0:.1f} s)")
    if run:
        mb.write_single(REG_CMD, CMD_RUN)
        log("앱 실행")


def make_transport(a):
    if a.sim:
        return PipeTransport(a.sim)
    return SerialTransport(a.port, a.baud, a.parity, a.stopbits)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    mk = sub.add_parser("mkimage", help="앱 바이너리 → 업데이트 이미지")
    mk.add_argument("input")
    mk.add_argument("output")
    mk.add_argument("--hw-id", type=lambda s: int(s, 0), required=True)
    mk.add_argument("--version", required=True, help="major.minor.patch")
    mk.add_argument("--slot-base", type=lambda s: int(s, 0), default=DEFAULT_SLOT_BASE)

    for name in ("info", "flash"):
        sp = sub.add_parser(name)
        if name == "flash":
            sp.add_argument("image")
            sp.add_argument("--no-run", action="store_true", help="완료 후 앱을 실행하지 않음")
        sp.add_argument("--port")
        sp.add_argument("--sim", help="시뮬레이터 명령 (테스트용)")
        sp.add_argument("--addr", type=int, default=1)
        sp.add_argument("--baud", type=int, default=19200)
        sp.add_argument("--parity", choices="NEO", default="E")
        sp.add_argument("--stopbits", type=int, choices=(1, 2), default=1)

    a = p.parse_args(argv)

    if a.cmd == "mkimage":
        with open(a.input, "rb") as f:
            payload = f.read()
        img = make_image(payload, a.hw_id, parse_version(a.version), a.slot_base)
        with open(a.output, "wb") as f:
            f.write(img)
        print(f"{a.output}: {len(img)} B (payload {len(payload)} B, CRC32 0x{zlib.crc32(payload):08X})")
        return 0

    if not (a.port or a.sim):
        p.error("--port 또는 --sim 이 필요합니다")
    t = make_transport(a)
    mb = ModbusClient(t, a.addr)
    if a.cmd == "info":
        mode = mb.read_holding(REG_ID, 1)[0]
        if mode == ID_BOOTLOADER:
            for k, v in read_info(mb).items():
                print(f"{k:12s} 0x{v:X}")
        else:
            print(f"mode id 0x{mode:04X} ({'app' if mode == ID_APP else 'unknown'})")
    else:
        with open(a.image, "rb") as f:
            flash(mb, f.read(), run=not a.no_run)
    if isinstance(t, PipeTransport):
        t.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
