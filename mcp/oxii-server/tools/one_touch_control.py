"""One-touch control helpers for OXII MCP server."""
from typing import Annotated

from pydantic import Field

from .common import get_rooms_with_devices, wait_for_status_update, _request


def _get_house_id(token: str) -> int:
    rooms = get_rooms_with_devices(token)
    if not rooms:
        raise ValueError("Không tìm thấy thông tin nhà")
    return int(rooms[0]["house_id"])


def one_touch_control_all_devices(
    token: Annotated[str, Field(description="Authentication token from OXII API")],
    command: Annotated[str, Field(description="Lệnh: 'on' hoặc 'off'")],
) -> str:
    """Switch all devices in the home on or off."""

    action = command.strip().upper()
    if action not in {"ON", "OFF"}:
        return "Lệnh one-touch không hợp lệ. Vui lòng dùng 'on' hoặc 'off'."

    try:
        house_id = _get_house_id(token)
    except Exception as exc:  # pragma: no cover
        return str(exc)

    code = "TURN_OFF_ALL_DEVICES" if action == "OFF" else "TURN_ON_ALL_DEVICES"
    text_command = "tắt" if action == "OFF" else "bật"

    try:
        _request(
            "POST",
            f"/api/app/house/{house_id}/one-touch/{code}/execute",
            token=token,
        )
    except Exception as exc:  # pragma: no cover
        return f"Không thể gửi lệnh one-touch: {exc}"

    def _checker() -> str | None:
        try:
            rooms = get_rooms_with_devices(token)
        except Exception:
            return None
        for room in rooms:
            for button in room.get("buttons", []):
                if button.get("remoteIRId") is None and button.get("status") != text_command:
                    return None
        return f"Tất cả thiết bị đã được {text_command} thành công"

    confirmation = wait_for_status_update(_checker)
    if confirmation:
        return confirmation
    return f"Đã gửi lệnh {text_command} tất cả thiết bị. Vui lòng kiểm tra trạng thái thiết bị."


def one_touch_control_by_type(
    token: Annotated[str, Field(description="Authentication token from OXII API")],
    device_type: Annotated[
        str,
        Field(description="Loại thiết bị: LIGHT, TV, CONDITIONER, FAN, HOT_COLD_SHOWER, SOCKET"),
    ],
    action: Annotated[str, Field(description="Lệnh: 'on' hoặc 'off'")],
) -> str:
    """Switch devices of a specific type on or off."""

    valid_device_types = {"LIGHT", "TV", "CONDITIONER", "FAN", "HOT_COLD_SHOWER", "SOCKET"}
    device_type_upper = device_type.strip().upper()
    if device_type_upper not in valid_device_types:
        return f"Loại thiết bị không hợp lệ. Các loại hợp lệ: {', '.join(sorted(valid_device_types))}"

    action_upper = action.strip().upper()
    if action_upper not in {"ON", "OFF"}:
        return "Hành động không hợp lệ. Các lựa chọn hợp lệ: on, off"

    try:
        house_id = _get_house_id(token)
    except Exception as exc:  # pragma: no cover
        return str(exc)

    code = f"TURN_{action_upper}_{device_type_upper}"
    expected_status = "bật" if action_upper == "ON" else "tắt"

    try:
        _request(
            "POST",
            f"/api/app/house/{house_id}/one-touch/{code}/execute",
            token=token,
        )
    except Exception as exc:  # pragma: no cover
        return f"Không thể gửi lệnh one-touch: {exc}"

    def _checker() -> str | None:
        try:
            rooms = get_rooms_with_devices(token)
        except Exception:
            return None
        for room in rooms:
            for button in room.get("buttons", []):
                if button.get("remoteIRId") is None and button.get("button_type") == device_type_upper:
                    if button.get("status") != expected_status:
                        return None
        return f"Tất cả thiết bị {device_type_upper} đã được {expected_status} thành công"

    confirmation = wait_for_status_update(_checker)
    if confirmation:
        return confirmation

    return (
        f"Đã gửi lệnh {action_upper.lower()} tất cả thiết bị {device_type_upper}. "
        "Vui lòng kiểm tra trạng thái thiết bị."
    )