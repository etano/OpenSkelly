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

Disconnect `12ft Skelly(Live)` from phones first. Only one audio source can own
the classic-Bluetooth connection at a time.

The included WirePlumber override selects 44.1 kHz SBC and enables an AVRCP
compatibility player. The default 2x microphone gain matches DecorPro.

Runtime state and logs are stored under `.skelly-live/`.

See [PROTOCOL.md](PROTOCOL.md) for reverse-engineered protocol details.

OpenSkelly is independent and is not affiliated with or endorsed by Home Depot
or the DecorPro application developers.
