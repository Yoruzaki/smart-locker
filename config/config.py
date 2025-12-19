from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[1]

# Core settings
FLASK_PORT = int(os.getenv("SMARTLOCKER_PORT", "5000"))
DEBUG = os.getenv("SMARTLOCKER_DEBUG", "false").lower() == "true"

# Database
DB_PATH = os.getenv("SMARTLOCKER_DB_PATH", str(BASE_DIR / "smartlocker.db"))

# Hardware / Serial
SERIAL_PORT = os.getenv("SMARTLOCKER_SERIAL_PORT", "/dev/ttyAMA0")
BAUD_RATE = int(os.getenv("SMARTLOCKER_BAUD_RATE", "115200"))
MOCK_HARDWARE = os.getenv("SMARTLOCKER_MOCK", "true").lower() == "true"
DOOR_CLOSE_TIMEOUT = int(os.getenv("SMARTLOCKER_DOOR_CLOSE_TIMEOUT", "25"))
DOOR_POLL_INTERVAL = float(os.getenv("SMARTLOCKER_DOOR_POLL_INTERVAL", "0.5"))

# Security
DEPOSIT_CODE_LENGTH = int(os.getenv("SMARTLOCKER_DEPOSIT_CODE_LENGTH", "6"))
WITHDRAW_CODE_LENGTH = int(os.getenv("SMARTLOCKER_WITHDRAW_CODE_LENGTH", "6"))

# Misc
RESERVED_LOCKERS = {16}
OPERATIONAL_LOCKERS = set(range(1, 16))
DEVICE_TYPE = "arduino_mega"



