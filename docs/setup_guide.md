# Smart Locker Delivery System - Setup Guide

## Prerequisites
- Raspberry Pi OS (Bullseye or newer)
- Python 3.9+
- Git
- Arduino IDE for uploading firmware
- Stable 5V power for Arduino + relays

## Raspberry Pi Setup
### Common steps (all editions)
```bash
sudo apt update && sudo apt install -y python3-pip python3-venv git
git clone https://github.com/Yoruzaki/smart-locker.git /home/pi/smartlocker
cd /home/pi/smartlocker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### If using Raspberry Pi OS Lite (64-bit, no desktop)
Install minimal X + Chromium for kiosk:
```bash
sudo apt install -y --no-install-recommends \
  xserver-xorg x11-xserver-utils xinit openbox \
  chromium xdotool unclutter
```
The Chromium binary on current releases is `chromium` (not `chromium-browser`).

### If using Raspberry Pi OS with Desktop
```bash
sudo apt install -y chromium-browser xdotool unclutter
```

## Environment
Create `/home/pi/smartlocker/.env` (optional) to override defaults:
```
SMARTLOCKER_SERIAL_PORT=/dev/ttyAMA0
SMARTLOCKER_MOCK=false
SMARTLOCKER_PORT=5000
```

## Run for development
```bash
source .venv/bin/activate
SMARTLOCKER_MOCK=true python app.py
```

## Systemd service
```bash
sudo cp config/smartlocker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable smartlocker
sudo systemctl start smartlocker
```

## Kiosk mode (Chromium)
Add to `/etc/xdg/lxsession/LXDE-pi/autostart`:
```
@/home/pi/smartlocker/config/kiosk_launch.sh
@unclutter -idle 0
```

## Arduino Mega wiring
- Pi GPIO14 (TX) -> Mega RX0 (Pin 0)
- Pi GPIO15 (RX) <- Mega TX0 (Pin 1)
- GND shared
- Relays: pins 22..52 (even)
- Door sensors: pins 23..53 (odd)
- Locker 16 is reserved (do not expose to users)

## Upload firmware
Open `arduino_firmware/locker_controller.ino` in Arduino IDE:
- Board: Arduino Mega 2560
- Port: (your USB port)
- Upload

## API quick reference
- `POST /api/v1/locker-hardware/open-deposit` `{closetId, lockerId}`
- `POST /api/v1/locker-hardware/close-deposit` `{closetId, lockerId, orderId?}`
- `POST /api/v1/locker-hardware/open-withdraw` `{closetId, lockerId, password}`
- `POST /api/v1/locker-hardware/close-withdraw` `{closetId, lockerId}`
- `POST /api/v1/customer/deposit` `{depositCode}`
- `POST /api/v1/customer/withdraw` `{password}`

## Troubleshooting
- Hardware not reachable: set `SMARTLOCKER_MOCK=true` to bypass during testing.
- Door not detected: verify sensor wiring and that sensors pull LOW when closed.
- Serial issues: confirm Pi UART enabled via `raspi-config` and correct `SMARTLOCKER_SERIAL_PORT`.
- Locker 16 requests rejected: it is reserved by design.

