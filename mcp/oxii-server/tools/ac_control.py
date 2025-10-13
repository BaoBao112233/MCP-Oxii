"""Air conditioner control tool for OXII MCP server."""
from typing import Annotated

from pydantic import Field

from .common import get_rooms_with_devices, _request


def control_air_conditioner(
    token: Annotated[str, Field(description="Authentication token from OXII API")],
    buttonId: Annotated[int, Field(description="ID của nút điều hòa")],
    power: Annotated[str, Field(description="Trạng thái nguồn: '1'/'on' để bật, '0'/'off' để tắt")],
    mode: Annotated[str, Field(description="Chế độ: '1'=auto, '2'=heat, '3'=cool, '4'=dry, '5'=fan", default="1")],
    temp: Annotated[str, Field(description="Nhiệt độ mục tiêu (16-32)", default="24")],
    fan_speed: Annotated[str, Field(description="Tốc độ quạt: '0'=auto, '1'=low, '2'=medium, '3'=high, '4'=turbo", default="0")],
    swing_h: Annotated[str, Field(description="Gió ngang: '1'=bật, '0'=tắt", default="0")],
    swing_v: Annotated[str, Field(description="Gió dọc: '1'=bật, '0'=tắt", default="0")],
) -> str:
    """Send a BLE mesh command to control an OXII air conditioner."""

    try:
        rooms = get_rooms_with_devices(token)
    except Exception as exc:  # pragma: no cover
        return f"Không thể lấy danh sách thiết bị: {exc}"

    button_info = None
    for room in rooms:
        for button in room.get("buttons", []):
            if button.get("buttonId") == buttonId:
                button_info = button
                break
        if button_info:
            break

    if not button_info:
        return f"Không tìm thấy thông tin của nút bấm với buttonId: {buttonId}"

    if button_info.get("label") != "CONDITIONER":
        return f"Thiết bị này không phải điều hòa. Loại thiết bị: {button_info.get('label')}"

    mesh_index = button_info.get("net_Index"), button_info.get("app_Index")
    if not all(mesh_index):
        return "Thiết bị chưa có thông tin mesh đầy đủ để điều khiển."

    payload = {
        "serial_number": [button_info.get("seriNumber")],
        "meshIndex": {
            "net_Index": mesh_index[0],
            "app_Index": mesh_index[1],
        },
        "command_type": 216,
        "data": {
            "Vendor": button_info.get("modelName"),
            "Power": power,
            "Mode": mode,
            "Temp": temp,
            "FanSpeed": fan_speed,
            "SwingH": swing_h,
            "SwingV": swing_v,
        },
    }

    try:
        _request("PUT", "/api/app/device/switch/ac-controls-mesh", token=token, json=payload)
    except Exception as exc:  # pragma: no cover
        return f"Không thể gửi lệnh điều khiển điều hòa: {exc}"

    return (
        "Đã gửi lệnh điều khiển điều hòa thành công "
        f"(nguồn: {power}, chế độ: {mode}, nhiệt độ: {temp}°C)."
    )