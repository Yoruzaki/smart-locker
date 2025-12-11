# Smart Locker Delivery System - Setup Guide

Follow these steps in order. Lite and Desktop editions both work; differences are called out.

## 1) Prerequisites
- Raspberry Pi OS Bullseye+ (Lite or Desktop, 64-bit recommended)
- Python 3.9+
- Git
- Arduino IDE (to flash the Mega)
- Stable 5V power for Arduino + relays

## 2) Enable UART (serial to Arduino)
```bash
sudo raspi-config nonint do_serial 1 0   # disable login shell on serial
sudo raspi-config nonint set_config_var enable_uart 1 /boot/config.txt
sudo reboot
```
After reboot, UART is typically `/dev/ttyAMA0`.

## 3) Install base packages
```bash
sudo apt update && sudo apt install -y python3-pip python3-venv git
```

### If using Raspberry Pi OS Lite (no desktop)
Install minimal X + Chromium for kiosk:
```bash
sudo apt install -y --no-install-recommends \
  xserver-xorg x11-xserver-utils xinit openbox \
  chromium xdotool unclutter
```
Browser binary on current releases: `chromium` (not `chromium-browser`).

### If using Raspberry Pi OS with Desktop
```bash
sudo apt install -y chromium-browser xdotool unclutter
```

## 4) Get the code and Python deps
```bash
git clone https://github.com/Yoruzaki/smart-locker.git /home/pi/smartlocker
cd /home/pi/smartlocker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 5) Configure environment (.env)
Create `/home/pi/smartlocker/.env` so the app knows your serial port and mode.

### Default (real hardware)
```bash
cat <<'EOF' > /home/pi/smartlocker/.env
SMARTLOCKER_SERIAL_PORT=/dev/ttyAMA0
SMARTLOCKER_MOCK=false
SMARTLOCKER_PORT=5000
EOF
```

### If Arduino is NOT connected yet (mock mode)
```bash
cat <<'EOF' > /home/pi/smartlocker/.env
SMARTLOCKER_SERIAL_PORT=/dev/ttyAMA0
SMARTLOCKER_MOCK=true
SMARTLOCKER_PORT=5000
EOF
```
Notes:
- Keep each setting on its own line.
- If your UART device differs (e.g., `/dev/ttyS0`), change `SMARTLOCKER_SERIAL_PORT`.

## 6) Run for development (manual)
```bash
cd /home/pi/smartlocker
source .venv/bin/activate
SMARTLOCKER_MOCK=true python app.py   # mock if Arduino not wired
```
Open `http://<pi-ip>:5000` to see the kiosk UI.

## 7) Install as a service (production)
```bash
cd /home/pi/smartlocker
sudo cp config/smartlocker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable smartlocker
sudo systemctl start smartlocker
sudo systemctl status smartlocker
```
Service runs the API on port 5000.

## 8) Kiosk auto-start (Chromium)
- Script: `config/kiosk_launch.sh` (auto-detects `chromium` vs `chromium-browser`).
- Make it executable: `chmod +x /home/pi/smartlocker/config/kiosk_launch.sh`

### On Raspberry Pi OS Desktop
Add to `/etc/xdg/lxsession/LXDE-pi/autostart`:
```
@/home/pi/smartlocker/config/kiosk_launch.sh
@unclutter -idle 0
```

### On Raspberry Pi OS Lite
1) Create Openbox autostart:
```bash
mkdir -p /home/pi/.config/openbox
cat <<'EOF' > /home/pi/.config/openbox/autostart
/home/pi/smartlocker/config/kiosk_launch.sh &
unclutter -idle 0 &
EOF
chmod +x /home/pi/.config/openbox/autostart
```
2) Start X + Openbox after login:
```bash
startx /usr/bin/openbox-session
```
Optional auto-start: add `startx /usr/bin/openbox-session` to `/home/pi/.bash_profile` so it launches on login.

### Auto-start everything at boot (service + kiosk)
1) Enable the backend service (already done in step 7):
```bash
sudo systemctl enable smartlocker
```
2) For Desktop edition: ensure the autostart entries above are present; the kiosk will launch after login.
3) For Lite edition: enable auto-login on console and auto-start X/Openbox:
```bash
sudo raspi-config nonint do_boot_behaviour B2   # Console autologin as pi
echo 'startx /usr/bin/openbox-session' >> /home/pi/.bash_profile
```
Reboot to verify: the service runs at boot, then the kiosk starts automatically.

## 9) Arduino Mega wiring (locker 1–15 only)
- Pi GPIO14 (TX) -> Mega RX0 (Pin 0)
- Pi GPIO15 (RX) <- Mega TX0 (Pin 1)
- GND shared
- Relays: pins 22..52 (even)
- Door sensors: pins 23..53 (odd)
- Locker 16 is reserved (not exposed to users)

## 10) Upload firmware to Arduino Mega
File: `arduino_firmware/locker_controller/locker_controller.ino`
- Board: Arduino Mega 2560
- Select the correct Port
- Upload via Arduino IDE

## 11) API quick reference
- `POST /api/v1/locker-hardware/open-deposit` `{closetId, lockerId}`
- `POST /api/v1/locker-hardware/close-deposit` `{closetId, lockerId, orderId?}`
- `POST /api/v1/locker-hardware/open-withdraw` `{closetId, lockerId, password}`
- `POST /api/v1/locker-hardware/close-withdraw` `{closetId, lockerId}`
- `POST /api/v1/customer/deposit` `{depositCode}`
- `POST /api/v1/customer/withdraw` `{password}`

## 12) Troubleshooting
- Hardware not reachable: set `SMARTLOCKER_MOCK=true` to bypass during testing.
- Door not detected: verify sensor wiring and that sensors pull LOW when closed.
- Serial issues: ensure UART is enabled (step 2) and `SMARTLOCKER_SERIAL_PORT` matches the Pi device.
- Locker 16 requests rejected: expected; it is reserved.

