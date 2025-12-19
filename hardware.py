import time
from typing import Optional

from config import config
from arduino_communicator import ArduinoCommunicator, DummyCommunicator
from database import set_door_state


class HardwareController:
    def __init__(self, cfg=config):
        self.cfg = cfg
        if cfg.MOCK_HARDWARE:
            self.client = DummyCommunicator()
        else:
            self.client = ArduinoCommunicator(cfg.SERIAL_PORT, cfg.BAUD_RATE)

    def ping(self) -> bool:
        return self.client.ping()

    def open_locker(self, locker_id: int) -> bool:
        return self.client.open_locker(locker_id)

    def is_door_closed(self, locker_id: int) -> Optional[bool]:
        state = self.client.read_sensor(locker_id)
        if state is None:
            return None
        closed = state.upper() == "CLOSED"
        set_door_state(locker_id, closed)
        return closed

    def wait_for_door_closed(self, locker_id: int, timeout: Optional[int] = None) -> bool:
        timeout = timeout or self.cfg.DOOR_CLOSE_TIMEOUT
        end_time = time.time() + timeout
        while time.time() < end_time:
            closed = self.is_door_closed(locker_id)
            if closed:
                return True
            time.sleep(self.cfg.DOOR_POLL_INTERVAL)
        return False



