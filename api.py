from datetime import datetime
import secrets
from flask import Blueprint, jsonify, request, current_app

from config import config
from database import (
    get_locker,
    set_locker_occupied,
    set_locker_available,
    save_order,
    update_order_status,
    get_order_by_deposit_code,
    get_order_by_withdraw_password,
    get_order_by_order_id,
    log_transaction,
    validate_operational_locker,
)
from device_config import RESERVED_LOCKERS

api_bp = Blueprint("api", __name__)


def generate_code(length: int) -> str:
    # Hex tokens are short and easy to read on a keypad
    return secrets.token_hex(length // 2)[:length]


def error_response(message: str, status: int = 400):
    return jsonify({"message": message, "success": False}), status


def _require_locker(locker_id: int):
    locker = get_locker(locker_id)
    if not locker:
        return None, error_response("Locker not found", 404)
    if locker_id in RESERVED_LOCKERS:
        return None, error_response("Locker is reserved", 403)
    return locker, None


@api_bp.route("/health", methods=["GET"])
def health():
    hardware = current_app.config["HARDWARE"]
    return jsonify({"status": "ok", "hardware": hardware.ping()})


@api_bp.route("/locker-hardware/open-deposit", methods=["POST"])
def open_deposit():
    data = request.get_json(force=True)
    locker_id = int(data.get("lockerId"))
    _ = data.get("closetId")  # currently single closet; reserved for future use
    locker, err = _require_locker(locker_id)
    if err:
        return err
    if locker["is_occupied"]:
        return error_response("Locker is occupied", 409)

    hardware = current_app.config["HARDWARE"]
    if not hardware.open_locker(locker_id):
        return error_response("Failed to open locker", 500)

    log_transaction(locker_id, "open_deposit")
    return jsonify({"lockerId": locker_id, "closetId": 1, "message": "Locker opened"})


@api_bp.route("/locker-hardware/close-deposit", methods=["POST"])
def close_deposit():
    data = request.get_json(force=True)
    locker_id = int(data.get("lockerId"))
    order_id = data.get("orderId")
    _ = data.get("closetId")

    try:
        validate_operational_locker(locker_id)
    except ValueError as exc:
        return error_response(str(exc), 403)

    hardware = current_app.config["HARDWARE"]
    if not hardware.wait_for_door_closed(locker_id):
        return error_response("Door did not close in time", 408)

    deposit_code = generate_code(config.DEPOSIT_CODE_LENGTH)
    withdraw_password = generate_code(config.WITHDRAW_CODE_LENGTH)
    save_order(locker_id, order_id, deposit_code, withdraw_password, status="deposited")
    set_locker_occupied(locker_id, order_id, password=withdraw_password)
    log_transaction(locker_id, "close_deposit", order_id, deposit_code, withdraw_password)

    return jsonify(
        {
            "closetId": 1,
            "lockerId": locker_id,
            "depositCode": deposit_code,
            "withdrawPassword": withdraw_password,
            "orderId": order_id,
            "message": "Deposit closed",
        }
    )


@api_bp.route("/locker-hardware/open-withdraw", methods=["POST"])
def open_withdraw():
    data = request.get_json(force=True)
    locker_id = int(data.get("lockerId"))
    password = data.get("password")

    locker, err = _require_locker(locker_id)
    if err:
        return err
    if not locker["is_occupied"]:
        return error_response("Locker is not occupied", 409)

    order = get_order_by_withdraw_password(password)
    if not order or order["locker_id"] != locker_id:
        return error_response("Invalid password", 401)

    hardware = current_app.config["HARDWARE"]
    if not hardware.open_locker(locker_id):
        return error_response("Failed to open locker", 500)

    log_transaction(locker_id, "open_withdraw", order["order_id"], withdraw_password=password)
    return jsonify(
        {"closetId": 1, "lockerId": locker_id, "orderId": order["order_id"], "message": "Locker opened"}
    )


@api_bp.route("/locker-hardware/close-withdraw", methods=["POST"])
def close_withdraw():
    data = request.get_json(force=True)
    locker_id = int(data.get("lockerId"))
    order_id = data.get("orderId")

    try:
        validate_operational_locker(locker_id)
    except ValueError as exc:
        return error_response(str(exc), 403)

    hardware = current_app.config["HARDWARE"]
    if not hardware.wait_for_door_closed(locker_id):
        return error_response("Door did not close in time", 408)

    set_locker_available(locker_id)
    update_order_status(order_id, status="withdrawn", withdrawn_at=datetime.utcnow())
    log_transaction(locker_id, "close_withdraw", order_id)
    return jsonify({"closetId": 1, "lockerId": locker_id, "message": "Locker closed"})


@api_bp.route("/customer/deposit", methods=["POST"])
def customer_deposit():
    data = request.get_json(force=True)
    deposit_code = data.get("depositCode")
    order = get_order_by_deposit_code(deposit_code)
    if not order:
        return error_response("Invalid code", 401)
    locker_id = order["locker_id"]

    try:
        validate_operational_locker(locker_id)
    except ValueError as exc:
        return error_response(str(exc), 403)

    hardware = current_app.config["HARDWARE"]
    if not hardware.open_locker(locker_id):
        return error_response("Failed to open locker", 500)

    closed = hardware.wait_for_door_closed(locker_id)
    update_order_status(
        order["order_id"],
        status="customer_deposited" if closed else order["status"],
        customer_deposited_at=datetime.utcnow() if closed else None,
    )
    log_transaction(locker_id, "customer_deposit", order["order_id"], deposit_code=deposit_code)
    msg = "Locker closed after deposit" if closed else "Locker opened"
    return jsonify({"lockerId": locker_id, "message": msg, "success": True})


@api_bp.route("/customer/withdraw", methods=["POST"])
def customer_withdraw():
    data = request.get_json(force=True)
    password = data.get("password")
    order = get_order_by_withdraw_password(password)
    if not order:
        return error_response("Invalid password", 401)
    locker_id = order["locker_id"]

    try:
        validate_operational_locker(locker_id)
    except ValueError as exc:
        return error_response(str(exc), 403)

    hardware = current_app.config["HARDWARE"]
    if not hardware.open_locker(locker_id):
        return error_response("Failed to open locker", 500)

    log_transaction(locker_id, "customer_withdraw", order["order_id"], withdraw_password=password)
    return jsonify(
        {"lockerId": locker_id, "orderId": order["order_id"], "message": "Locker opened", "success": True}
    )


