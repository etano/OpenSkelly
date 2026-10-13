# Protocol notes

OpenSkelly was derived by observing DecorPro's behavior and inspecting its
Android client. A Skelly exposes two Bluetooth endpoints:

- `12ft Skelly`: BLE control service `AE00`
- `12ft Skelly(Live)`: classic Bluetooth A2DP audio sink

The BLE write characteristic is `AE01` (handle `0x0082`, write without
response); notifications arrive on `AE02`. Frames begin with `AA`, contain an
opcode and an eight-byte padded payload, and end with CRC-8 (reflected
polynomial `0x8C`).

Live-mode sequence:

1. Stop onboard-file playback (`C6`).
2. Enable the classic radio (`FD 01`).
3. Connect the A2DP endpoint.
4. Select classic Bluetooth audio (`FE 01`).
5. Start the audio stream.
6. Enter Live animation (`FC 01`).
7. Apply hardware volume (`FA`).

Pairing credentials are intentionally not included. Device addresses are unique
and are discovered during `openskelly configure`.

Lighting commands use these opcodes:

- `F3`: brightness (`0`-`100`)
- `F4`: RGB color
- `F5`: selected channel
- `F6`: animation speed
- `F9`: eye pattern

The protocol provides six RGB channel numbers (`0`-`5`) plus `FF` for all.
Testing on a 12 ft. Skelly found one visible controllable zone: channel `0` is
the chest light. Channels `1` through `3` produced no visible change; channels
`4` and `5` remain untested.

The tested hardware required SBC at 44.1 kHz. At 48 kHz the transport appeared
active but produced no audio. Audio also needs sufficient signal level to cross
the mouth-animation threshold.
