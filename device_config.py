LOCKERS = [
    {"id": 1, "relay_pin": 22, "sensor_pin": 23, "reserved": False},
    {"id": 2, "relay_pin": 24, "sensor_pin": 25, "reserved": False},
    {"id": 3, "relay_pin": 26, "sensor_pin": 27, "reserved": False},
    {"id": 4, "relay_pin": 28, "sensor_pin": 29, "reserved": False},
    {"id": 5, "relay_pin": 30, "sensor_pin": 31, "reserved": False},
    {"id": 6, "relay_pin": 32, "sensor_pin": 33, "reserved": False},
    {"id": 7, "relay_pin": 34, "sensor_pin": 35, "reserved": False},
    {"id": 8, "relay_pin": 36, "sensor_pin": 37, "reserved": False},
    {"id": 9, "relay_pin": 38, "sensor_pin": 39, "reserved": False},
    {"id": 10, "relay_pin": 40, "sensor_pin": 41, "reserved": False},
    {"id": 11, "relay_pin": 42, "sensor_pin": 43, "reserved": False},
    {"id": 12, "relay_pin": 44, "sensor_pin": 45, "reserved": False},
    {"id": 13, "relay_pin": 46, "sensor_pin": 47, "reserved": False},
    {"id": 14, "relay_pin": 48, "sensor_pin": 49, "reserved": False},
    {"id": 15, "relay_pin": 50, "sensor_pin": 51, "reserved": False},
    {"id": 16, "relay_pin": 52, "sensor_pin": 53, "reserved": True},  # Reserved for enclosure
]

RESERVED_LOCKERS = {locker["id"] for locker in LOCKERS if locker.get("reserved")}
OPERATIONAL_LOCKERS = {locker["id"] for locker in LOCKERS if not locker.get("reserved")}
DEVICE_TYPE = "arduino_mega"


