"""One-touch control helpers for OXII MCP server."""
from typing import Annotated

from pydantic import Field

from .common import get_rooms_with_devices, wait_for_status_update, _request
import time
from .mockup_data import MOCK_ROOMS, BUTTON_STATES

def one_touch_control_all_devices(
    token: Annotated[str, Field(description="Authentication token from OXII API")],
    command: Annotated[str, Field(description="Lệnh: 'on' hoặc 'off'")],
) -> str:
    """[MOCK] Switch all devices in the home on or off."""
    
    action = command.strip().upper()
    if action not in {"ON", "OFF"}:
        return "Lệnh one-touch không hợp lệ. Vui lòng dùng 'on' hoặc 'off'."
    
    text_command = "tắt" if action == "OFF" else "bật"
    
    print(f"[MOCK] One-touch control ALL devices -> {text_command}")
    
    # Update all button states
    for button_id in BUTTON_STATES:
        BUTTON_STATES[button_id] = text_command
    
    time.sleep(0.5)
    
    return f"Tất cả thiết bị đã được {text_command} thành công"


def one_touch_control_by_type(
    token: Annotated[str, Field(description="Authentication token from OXII API")],
    device_type: Annotated[
        str,
        Field(description="Loại thiết bị: LIGHT, TV, CONDITIONER, FAN, HOT_COLD_SHOWER, SOCKET"),
    ],
    action: Annotated[str, Field(description="Lệnh: 'on' hoặc 'off'")],
) -> str:
    """[MOCK] Switch devices of a specific type on or off."""
    
    valid_device_types = {"LIGHT", "TV", "CONDITIONER", "FAN", "HOT_COLD_SHOWER", "SOCKET"}
    device_type_upper = device_type.strip().upper()
    
    if device_type_upper not in valid_device_types:
        return f"Loại thiết bị không hợp lệ. Các loại hợp lệ: {', '.join(sorted(valid_device_types))}"
    
    action_upper = action.strip().upper()
    if action_upper not in {"ON", "OFF"}:
        return "Hành động không hợp lệ. Các lựa chọn hợp lệ: on, off"
    
    expected_status = "bật" if action_upper == "ON" else "tắt"
    
    print(f"[MOCK] One-touch control {device_type_upper} -> {expected_status}")
    
    # Update states for matching device types
    count = 0
    for room in MOCK_ROOMS:
        for button in room.get("buttons", []):
            if button.get("button_type") == device_type_upper:
                button_id = button.get("buttonId")
                if button_id in BUTTON_STATES:
                    BUTTON_STATES[button_id] = expected_status
                    count += 1
    
    time.sleep(0.5)
    
    return f"Tất cả thiết bị {device_type_upper} ({count} thiết bị) đã được {expected_status} thành công"

