"""부트로더 코어(C, 호스트 시뮬레이터) + 업데이트 도구 통합 테스트.

실행: python3 -m unittest discover -s tests
"""

import os
import random
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import fwupdate as fw  # noqa: E402

SIM = os.path.join(ROOT, "firmware", "build", "bl_host")
HW_ID = 1


def setUpModule():
    subprocess.run(["make", "-s", "-C", os.path.join(ROOT, "firmware")], check=True)


def quiet(*_):
    pass


class BootloaderTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.flash_file = os.path.join(self.tmp.name, "flash.bin")
        rnd = random.Random(1234)
        self.payload = bytes(rnd.randrange(256) for _ in range(30001))  # 홀수 길이, 마지막 블록 부분
        self.image = fw.make_image(self.payload, HW_ID, fw.parse_version("1.2.3"))

    def tearDown(self):
        self.tmp.cleanup()

    def start(self, app=False):
        cmd = f"{SIM} --flash {self.flash_file}" + (" --start-app" if app else "")
        t = fw.PipeTransport(cmd)
        return t, fw.ModbusClient(t, 1, retries=0)

    def read_flash(self):
        with open(self.flash_file, "rb") as f:
            return f.read()

    def begin(self, mb, size):
        mb.write_multiple(fw.REG_CMD, [fw.CMD_BEGIN, size >> 16, size & 0xFFFF])

    def send_block(self, mb, image, i):
        chunk = image[i * 128:(i + 1) * 128]
        if len(chunk) % 2:
            chunk += b"\xFF"
        mb.write_multiple(fw.REG_DATA, [i] + list(struct.unpack(f">{len(chunk) // 2}H", chunk)))

    def test_crc16_reference_vector(self):
        self.assertEqual(fw.crc16_modbus(b"123456789"), 0x4B37)

    def test_full_update_from_app_mode(self):
        t, mb = self.start(app=True)
        fw.flash(mb, self.image, log=quiet)
        self.assertEqual(t.close(), 0)  # 시뮬레이터: 유효한 앱으로 점프하면 0
        flash = self.read_flash()
        self.assertEqual(flash[:fw.HDR_AREA], self.image[:fw.HDR_AREA])
        self.assertEqual(flash[fw.HDR_AREA:fw.HDR_AREA + len(self.payload)], self.payload)

        t, mb = self.start()
        info = fw.read_info(mb)
        t.close()
        self.assertEqual(info["id"], fw.ID_BOOTLOADER)
        self.assertEqual(info["app_valid"], 1)
        self.assertEqual(info["app_version"], fw.parse_version("1.2.3"))

    def test_wrong_hw_id_rejected_by_device(self):
        bad = fw.make_image(self.payload, HW_ID + 1, 1)
        t, mb = self.start()
        self.begin(mb, len(bad))
        with self.assertRaises(fw.ModbusError):
            self.send_block(mb, bad, 0)
        self.assertEqual(fw.read_info(mb)["error"], 7)
        t.close()

    def test_retry_same_block_is_idempotent_and_order_enforced(self):
        t, mb = self.start()
        self.begin(mb, len(self.image))
        self.send_block(mb, self.image, 0)
        self.send_block(mb, self.image, 0)  # 응답 유실 후 재전송 가정
        for i in range(1, 6):
            self.send_block(mb, self.image, i)
        self.send_block(mb, self.image, 5)
        with self.assertRaises(fw.ModbusError):
            self.send_block(mb, self.image, 7)  # 건너뛰기
        info = fw.read_info(mb)
        self.assertEqual((info["next_block"], info["error"]), (6, 3))
        with self.assertRaises(fw.ModbusError):
            mb.write_single(fw.REG_CMD, fw.CMD_FINISH)  # 미완료
        self.assertEqual(fw.read_info(mb)["error"], 9)
        t.close()

    def test_corrupted_payload_fails_crc_and_app_stays_invalid(self):
        bad = bytearray(self.image)
        bad[-100] ^= 0x01
        t, mb = self.start()
        self.begin(mb, len(bad))
        for i in range((len(bad) + 127) // 128):
            self.send_block(mb, bytes(bad), i)
        with self.assertRaises(fw.ModbusError):
            mb.write_single(fw.REG_CMD, fw.CMD_FINISH)
        info = fw.read_info(mb)
        self.assertEqual((info["error"], info["app_valid"]), (8, 0))
        with self.assertRaises(fw.ModbusError):
            mb.write_single(fw.REG_CMD, fw.CMD_RUN)
        t.close()

    def test_interrupted_update_leaves_app_invalid(self):
        t, mb = self.start()
        fw.flash(mb, self.image, run=False, log=quiet)
        t.close()

        # 새 업데이트 도중 전원 차단 → 헤더 미기록 → 부트로더에 머묾
        new = fw.make_image(self.payload[::-1], HW_ID, fw.parse_version("1.3.0"))
        t, mb = self.start()
        self.begin(mb, len(new))
        for i in range(50):
            self.send_block(mb, new, i)
        t.close()

        t, mb = self.start()
        self.assertEqual(fw.read_info(mb)["app_valid"], 0)
        fw.flash(mb, new, log=quiet)  # 재시도로 복구
        self.assertEqual(t.close(), 0)

    def test_broadcast_and_other_address_ignored(self):
        t, _ = self.start()
        for addr in (0, 2):
            mb = fw.ModbusClient(t, addr, retries=0)
            with self.assertRaises(TimeoutError):
                mb.read_holding(0, 1)
        t.close()


if __name__ == "__main__":
    unittest.main()
