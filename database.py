import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import config
from device_config import LOCKERS, RESERVED_LOCKERS

DB_PATH = Path(config.DB_PATH)


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS lockers (
                id INTEGER PRIMARY KEY,
                closet_id INTEGER,
                is_occupied BOOLEAN DEFAULT 0,
                door_closed BOOLEAN DEFAULT 1,
                password TEXT,
                order_id INTEGER,
                device_type TEXT,
                relay_pin INTEGER,
                sensor_pin INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER UNIQUE,
                locker_id INTEGER,
                deposit_code TEXT,
                withdraw_password TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                customer_deposited_at TIMESTAMP,
                withdrawn_at TIMESTAMP
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                locker_id INTEGER,
                order_id INTEGER,
                action TEXT,
                deposit_code TEXT,
                withdraw_password TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        for locker in LOCKERS:
            cur.execute(
                """
                INSERT OR IGNORE INTO lockers (id, closet_id, is_occupied, door_closed, password,
                    order_id, device_type, relay_pin, sensor_pin)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    locker["id"],
                    1,
                    0,
                    1,
                    None,
                    None,
                    locker.get("device_type", "arduino_mega"),
                    locker["relay_pin"],
                    locker["sensor_pin"],
                ),
            )
        conn.commit()


def get_locker(locker_id: int) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM lockers WHERE id = ?", (locker_id,))
        return cur.fetchone()


def set_locker_occupied(locker_id: int, order_id: Optional[int], password: Optional[str] = None):
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE lockers SET is_occupied = 1, order_id = ?, password = ?, updated_at = ?
            WHERE id = ?;
            """,
            (order_id, password, datetime.utcnow(), locker_id),
        )


def set_locker_available(locker_id: int):
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE lockers
            SET is_occupied = 0, order_id = NULL, password = NULL, updated_at = ?, door_closed = 1
            WHERE id = ?;
            """,
            (datetime.utcnow(), locker_id),
        )


def set_door_state(locker_id: int, closed: bool):
    with get_connection() as conn:
        conn.execute(
            "UPDATE lockers SET door_closed = ?, updated_at = ? WHERE id = ?;",
            (1 if closed else 0, datetime.utcnow(), locker_id),
        )


def save_order(
    locker_id: int,
    order_id: Optional[int],
    deposit_code: str,
    withdraw_password: str,
    status: str,
):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO orders (order_id, locker_id, deposit_code, withdraw_password, status)
            VALUES (?, ?, ?, ?, ?);
            """,
            (order_id, locker_id, deposit_code, withdraw_password, status),
        )


def update_order_status(
    order_id: Optional[int],
    status: str,
    customer_deposited_at: Optional[datetime] = None,
    withdrawn_at: Optional[datetime] = None,
):
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE orders
            SET status = COALESCE(?, status),
                customer_deposited_at = COALESCE(?, customer_deposited_at),
                withdrawn_at = COALESCE(?, withdrawn_at)
            WHERE order_id = ?;
            """,
            (status, customer_deposited_at, withdrawn_at, order_id),
        )


def get_order_by_deposit_code(code: str) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM orders WHERE deposit_code = ?;", (code,))
        return cur.fetchone()


def get_order_by_withdraw_password(password: str) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM orders WHERE withdraw_password = ?;", (password,))
        return cur.fetchone()


def get_order_by_order_id(order_id: int) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM orders WHERE order_id = ?;", (order_id,))
        return cur.fetchone()


def log_transaction(
    locker_id: int,
    action: str,
    order_id: Optional[int] = None,
    deposit_code: Optional[str] = None,
    withdraw_password: Optional[str] = None,
):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO transactions (locker_id, order_id, action, deposit_code, withdraw_password)
            VALUES (?, ?, ?, ?, ?);
            """,
            (locker_id, order_id, action, deposit_code, withdraw_password),
        )


def validate_operational_locker(locker_id: int):
    if locker_id in RESERVED_LOCKERS:
        raise ValueError("Locker is reserved and cannot be used in normal flow.")



