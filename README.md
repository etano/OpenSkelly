# OpenSkelly

Open-source Linux controller and Live-mode audio bridge for Home Depot's 12 ft.
Skelly. It reproduces the DecorPro Live sequence and routes a PipeWire
microphone to `12ft Skelly(Live)` with speech-driven mouth movement.

## Requirements

Linux with BlueZ, PipeWire, WirePlumber, `bluetoothctl`, `gatttool`,
`pw-loopback`, and `wpctl`.

## Setup

Pair `12ft Skelly(Live)` in `bluetoothctl` using the PIN supplied with your
device or shown by DecorPro.

```bash
mkdir -p ~/.config/wireplumber/wireplumber.conf.d
cp config/90-openskelly.conf ~/.config/wireplumber/wireplumber.conf.d/
systemctl --user restart wireplumber
./openskelly configure
```

If discovery fails, use `configure --ble-mac AA:... --live-mac BB:...`.

## Usage

```bash
./openskelly start
./openskelly status
./openskelly stop
```

Control the RGB chest light with a six-digit hex color or brightness from 0 to
100:

```bash
./openskelly lights color ff0000
./openskelly lights color 8000ff --brightness 50
./openskelly lights brightness 25
./openskelly lights off
```

The friendly channel name `chest` is the default. `--channel all` and numeric
channels `0` through `5` are also accepted for compatible hardware variants;
on the tested 12 ft. Skelly, only protocol channel `0` controlled a visible
light. Stop microphone Live mode before changing lights.

Select any of the 20 eye patterns built into Skelly's firmware:

```bash
./openskelly eyes set 1
./openskelly eyes set 20
```

Eye artwork cannot be uploaded through the known DecorPro Bluetooth protocol;
it only selects numbered firmware presets. Stop microphone Live mode before
changing the eyes.

To play any audio file with synchronized mouth animation:

```bash
./openskelly play speech.wav
```

OpenSkelly accepts any format supported by FFmpeg. It normalizes and converts
the input to 44.1 kHz stereo, adds a short lead-in so Bluetooth connection
sounds do not overlap playback, animates the mouth, and disconnects afterward.
This keeps OpenSkelly independent of any particular TTS engine; generate the
audio with your preferred voice system first. Stop microphone Live mode before
using `play`.

Disconnect `12ft Skelly(Live)` from phones first. Only one audio source can own
the classic-Bluetooth connection at a time.

The included WirePlumber override selects 44.1 kHz SBC and enables an AVRCP
compatibility player. The default 2x microphone gain matches DecorPro.

Runtime state and logs are stored under `.skelly-live/`.

See [PROTOCOL.md](PROTOCOL.md) for reverse-engineered protocol details.

OpenSkelly is independent and is not affiliated with or endorsed by Home Depot
or the DecorPro application developers.
