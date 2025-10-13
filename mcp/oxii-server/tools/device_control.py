"""Device listing and switch control tools for OXII MCP server."""
from typing import Annotated, Dict, Iterable, Optional, Any

from pydantic import Field

from .common import get_device_properties, get_rooms_with_devices, serialise_rooms, wait_for_status_update, _request


def get_device_list(
    token: Annotated[str, Field(description="Authentication token from OXII API")]
) -> str:
    """Return the list of rooms, devices, and remote buttons as formatted JSON."""

    try:
        rooms = get_rooms_with_devices(token)
        return serialise_rooms(rooms)
    except Exception as exc:  # pragma: no cover - surfaced to agent
        return f"Error getting device list: {exc}"


def _iter_buttons(rooms: Iterable[Dict[str, Any]]) -> Iterable[Dict[str, Any]]:
    for room in rooms:
        for button in room.get("buttons", []):
            yield button


def switch_device_control(
    token: Annotated[str, Field(description="Authentication token from OXII API")],
    buttonId: Annotated[int, Field(description="ID of the button to control")],
    action: Annotated[str, Field(description="Action: 'on' or 'off'")],
) -> str:
    """Toggle a switch device on or off."""

    action_normalised = action.strip().lower()
    if action_normalised not in {"on", "off"}:
        return "Hành động không hợp lệ. Vui lòng chọn 'on' hoặc 'off'."

    try:
        rooms = get_rooms_with_devices(token)
    except Exception as exc:  # pragma: no cover
        return f"Không thể lấy danh sách thiết bị: {exc}"

    button = next((b for b in _iter_buttons(rooms) if b.get("buttonId") == buttonId), None)
    if not button:
        return f"Không tìm thấy thông tin của nút bấm với buttonId: {buttonId}"

    device_id = button.get("deviceId")
    if device_id is None:
        return "Không tìm thấy thiết bị tương ứng với nút bấm này."

    try:
        device = get_device_properties(token, int(device_id))
    except Exception as exc:  # pragma: no cover
        return f"Không thể truy vấn thông tin thiết bị: {exc}"

    if device.get("status") == 2 and device.get("joinMesh") == 0:
        return "Thiết bị đang ngoại tuyến, không thể điều khiển."

    serial = device.get("seriNumber")
    button_code = (button.get("button_code") or "")[-2:]
    if not serial or len(button_code) != 2:
        return "Thiếu thông tin serial hoặc mã nút để điều khiển."

    payload = {
        "serial_number": serial,
        "command_type": int(f"2{button_code}"),
        "data": 1 if action_normalised == "on" else 0,
    }

    try:
        _request("PUT", "/api/app/device/switch/on-off-controls-v2", token=token, json=payload)
    except Exception as exc:  # pragma: no cover
        return f"Không thể gửi lệnh điều khiển: {exc}"

    expected_status = "bật" if action_normalised == "on" else "tắt"

    def _checker() -> Optional[str]:
        try:
            refreshed = get_rooms_with_devices(token)
        except Exception:
            return None
        for refreshed_room in refreshed:
            for refreshed_button in refreshed_room.get("buttons", []):
                if refreshed_button.get("buttonId") == buttonId and refreshed_button.get("status") == expected_status:
                    return f"Thiết bị {refreshed_button.get('name')} đã được {expected_status} thành công"
        return None

    confirmation = wait_for_status_update(_checker)
    if confirmation:
        return confirmation

    return f"Đã gửi lệnh {expected_status} tới thiết bị {button.get('name')}. Vui lòng kiểm tra trạng thái sau ít phút."