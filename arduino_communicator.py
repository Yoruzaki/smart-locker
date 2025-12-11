import time
from typing import Optional

try:
    import serial  # type: ignore
except ImportError:
    serial = None


class ArduinoCommunicator:
    def __init__(self, port: str, baud_rate: int, timeout: float = 1.0):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.serial = None
        self._connect()

    def _connect(self):
        if not serial:
            return
        if self.serial and self.serial.is_open:
            return
        self.serial = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
        time.sleep(2)  # allow Arduino bootloader to settle

    def send_command(self, command: str) -> Optional[str]:
        if not serial:
            return None
        self._connect()
        self.serial.write((command + "\n").encode("utf-8"))
        self.serial.flush()
        response = self.serial.readline().decode("utf-8").strip()
        return response or None

    def open_locker(self, locker_id: int) -> bool:
        resp = self.send_command(f"OPEN:{locker_id}")
        return resp == "OK"

    def read_sensor(self, locker_id: int) -> Optional[str]:
        return self.send_command(f"READ:{locker_id}")

    def status(self) -> Optional[str]:
        return self.send_command("STATUS")

    def ping(self) -> bool:
        return self.send_command("PING") == "OK"


class DummyCommunicator:
    """Fallback communicator for development without hardware."""

    def __init__(self):
        self.doors_closed = {i: True for i in range(1, 17)}

    def open_locker(self, locker_id: int) -> bool:
        # Simulate door opening then closing after a short delay
        self.doors_closed[locker_id] = False
        time.sleep(0.5)
        self.doors_closed[locker_id] = True
        return True

    def read_sensor(self, locker_id: int) -> str:
        return "CLOSED" if self.doors_closed.get(locker_id, True) else "OPEN"

    def status(self) -> str:
        return "OK"

    def ping(self) -> bool:
        return True


