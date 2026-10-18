import argparse
import runpy
import unittest
from pathlib import Path


MODULE = runpy.run_path(str(Path(__file__).parents[1] / "openskelly"), run_name="openskelly_test")


class ProtocolTests(unittest.TestCase):
    def test_known_light_frames(self):
        frame = MODULE["protocol_frame"]
        self.assertEqual(
            frame(0xF3, bytes.fromhex("0064ffffffff0000")),
            "aaf30064ffffffff000046",
        )
        self.assertEqual(
            frame(0xF4, bytes.fromhex("00ff000000ffffffff00")),
            "aaf400ff000000ffffffff00a2",
        )

    def test_known_eye_frames(self):
        frame = MODULE["protocol_frame"]
        self.assertEqual(frame(0xF9, bytes.fromhex("0100ffffffff00")), "aaf90100ffffffff00ce")
        self.assertEqual(frame(0xF9, bytes.fromhex("0800ffffffff00")), "aaf90800ffffffff0002")

    def test_light_channel_aliases_and_range(self):
        parse = MODULE["light_channel"]
        self.assertEqual(parse("chest"), 0)
        self.assertEqual(parse("all"), 0xFF)
        self.assertEqual(parse("5"), 5)
        with self.assertRaises(argparse.ArgumentTypeError):
            parse("6")


class AudioRoutingTests(unittest.TestCase):
    def test_sink_name(self):
        self.assertEqual(
            MODULE["sink_name"]("13:C0:02:6E:21:3C"),
            "bluez_output.13_C0_02_6E_21_3C.1",
        )

    def test_finds_only_spotify_sink_inputs(self):
        output = """Sink Input #14
    Properties:
        application.process.binary = "python3"
Sink Input #27
    Properties:
        application.process.binary = "spotifyd"
Sink Input #31
    Properties:
        application.process.binary = "spotifyd"
"""
        self.assertEqual(MODULE["spotify_sink_input_ids"](output), ["27", "31"])


if __name__ == "__main__":
    unittest.main()
