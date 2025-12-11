# Smart Locker Delivery System

Raspberry Pi–hosted locker controller with Arduino Mega hardware, REST API for the admin system, and a bilingual (Arabic/French) touchscreen kiosk UI for customers.

## Features
- Flask API with 6 endpoints (admin + customer) and health check
- SQLite persistence for lockers, orders, transactions
- Hardware abstraction with UART to Arduino Mega or mock mode for development
- Locker 16 reserved and excluded from customer/admin normal flows
- Touch-friendly kiosk UI (800×480) with RTL Arabic/French toggle
- Arduino Mega firmware for 16 relays/sensors on pins 22–53

## Repository Layout
- `app.py` – Flask app factory/entrypoint
- `api.py` – API routes
- `hardware.py`, `arduino_communicator.py` – hardware abstraction / serial
- `database.py`, `device_config.py`, `config/` – DB + config
- `static/`, `templates/` – kiosk UI
- `arduino_firmware/locker_controller/locker_controller.ino` – Mega sketch
- `docs/setup_guide.md` – full setup and wiring

## Quickstart (dev, mock hardware)
```bash
cd smartlocker
python -m venv .venv
.venv\\Scripts\\activate  # Windows
pip install -r requirements.txt
set SMARTLOCKER_MOCK=true
python app.py
```
Open `http://localhost:5000` for the kiosk UI. API base: `http://localhost:5000/api/v1`.

## Hardware Deployment (Pi + Mega)
1) Follow `docs/setup_guide.md` for Raspberry Pi setup, env, and systemd service.  
2) Upload `arduino_firmware/locker_controller/locker_controller.ino` to the Arduino Mega (pins 22–53 wired as specified).  
3) Set `SMARTLOCKER_MOCK=false` and correct `SMARTLOCKER_SERIAL_PORT` (e.g., `/dev/ttyAMA0`).  
4) Start the service and kiosk script; verify `/api/v1/health`.

## Key API Endpoints
- `POST /api/v1/locker-hardware/open-deposit` `{closetId, lockerId}`
- `POST /api/v1/locker-hardware/close-deposit` `{closetId, lockerId, orderId?}`
- `POST /api/v1/locker-hardware/open-withdraw` `{closetId, lockerId, password}`
- `POST /api/v1/locker-hardware/close-withdraw` `{closetId, lockerId}`
- `POST /api/v1/customer/deposit` `{depositCode}`
- `POST /api/v1/customer/withdraw` `{password}`

Locker 16 is rejected (reserved).

## Tests (manual)
- Mock mode: exercise deposit/withdraw APIs and confirm UI flows.
- Hardware: open/close per locker, sensor closes, reserved locker rejection, PING/STATUS responses.

## Notes
- Uses `waitress` for production (`pip install -r requirements.txt`).
- Systemd unit: `config/smartlocker.service`; kiosk launcher: `config/kiosk_launch.sh`.

