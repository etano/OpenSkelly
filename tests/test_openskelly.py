import argparse
import runpy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, call, patch


MODULE = runpy.run_path(str(Path(__file__).parents[1] / "openskelly"), run_name="openskelly_test")
GLOBALS = MODULE["ensure_audio_sink"].__globals__


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

    def test_existing_sink_does_not_restart_audio(self):
        with (
            patch.dict(GLOBALS, {
                "wait_for_audio_sink": Mock(),
                "restart_audio_stack": Mock(),
            }),
        ):
            MODULE["ensure_audio_sink"](Mock(), "AA:BB")
            GLOBALS["restart_audio_stack"].assert_not_called()

    def test_missing_sink_restarts_audio_once_without_reconnecting_when_adopted(self):
        missing = MODULE["AudioSinkUnavailable"]("missing")
        with patch.dict(GLOBALS, {
            "wait_for_audio_sink": Mock(side_effect=[missing, None]),
            "restart_audio_stack": Mock(),
            "connect_live": Mock(),
        }):
            MODULE["ensure_audio_sink"](Mock(), "AA:BB")
            GLOBALS["restart_audio_stack"].assert_called_once_with()
            GLOBALS["connect_live"].assert_not_called()
            self.assertEqual(
                GLOBALS["wait_for_audio_sink"].call_args_list,
                [call("AA:BB"), call("AA:BB", attempts=40)],
            )

    def test_reconnects_once_when_reset_cannot_adopt_existing_connection(self):
        missing = MODULE["AudioSinkUnavailable"]("missing")
        with patch.dict(GLOBALS, {
            "wait_for_audio_sink": Mock(side_effect=[missing, missing, None]),
            "restart_audio_stack": Mock(),
            "connect_live": Mock(),
            "run_checked": Mock(),
        }):
            gatt = Mock()
            MODULE["ensure_audio_sink"](gatt, "AA:BB")
            GLOBALS["restart_audio_stack"].assert_called_once_with()
            GLOBALS["connect_live"].assert_called_once_with(gatt, "AA:BB")
            GLOBALS["run_checked"].assert_called_once_with(
                "bluetoothctl", "disconnect", "AA:BB", timeout=10,
            )

    def test_audio_stack_reset_has_cooldown(self):
        with tempfile.TemporaryDirectory() as temp:
            reset_file = Path(temp) / "audio-reset"
            reset_file.write_text("75\n")
            with (
                patch.dict(GLOBALS, {"AUDIO_RESET_FILE": reset_file}),
                patch.object(GLOBALS["time"], "monotonic", return_value=100.0),
                patch.object(GLOBALS["subprocess"], "run") as run,
            ):
                with self.assertRaisesRegex(RuntimeError, "already reset recently"):
                    MODULE["restart_audio_stack"]()
                run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
