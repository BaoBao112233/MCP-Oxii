"""Device listing and switch control tools for OXII MCP server."""
from typing import Annotated, Dict, Iterable, Optional, Any
import json
import time
from pydantic import Field

from .common import get_device_properties, get_rooms_with_devices, serialise_rooms, wait_for_status_update, _request
from .mockup_data import MOCK_ROOMS, BUTTON_STATES

def get_device_list(
    token: Annotated[str, Field(description="Authentication token from OXII API")]
) -> str:
    """[MOCK] Return the list of rooms, devices, and remote buttons as formatted JSON."""
    
    print(f"[MOCK] Getting device list with token: {token[:20]}...")
    
    # Update button states in mock data
    for room in MOCK_ROOMS:
        for button in room.get("buttons", []):
            button_id = button.get("buttonId")
            if button_id in BUTTON_STATES:
                button["status"] = BUTTON_STATES[button_id]
    
    return json.dumps(MOCK_ROOMS, ensure_ascii=False, indent=4)


def switch_device_control(
    token: Annotated[str, Field(description="Authentication token from OXII API")],
    buttonId: Annotated[int, Field(description="ID of the button to control")],
    action: Annotated[str, Field(description="Action: 'on' or 'off'")],
) -> str:
    """[MOCK] Toggle a switch device on or off."""
    
    action_normalised = action.strip().lower()
    if action_normalised not in {"on", "off"}:
        return "Hành động không hợp lệ. Vui lòng chọn 'on' hoặc 'off'."
    
    # Find button
    button_found = None
    for room in MOCK_ROOMS:
        for button in room.get("buttons", []):
            if button.get("buttonId") == buttonId:
                button_found = button
                break
        if button_found:
            break
    
    if not button_found:
        return f"Không tìm thấy thông tin của nút bấm với buttonId: {buttonId}"
    
    # Get current status
    current_status = BUTTON_STATES.get(buttonId, "tắt")
    
    # Simulate control
    expected_status = "bật" if action_normalised == "on" else "tắt"
    BUTTON_STATES[buttonId] = expected_status
    
    button_name = button_found.get('name', 'thiết bị')
    print(f"[MOCK] Controlling device {button_name}: {current_status} -> {expected_status}")
    
    # Simulate delay for state change
    time.sleep(0.5)
    
    # Verify status change
    new_status = BUTTON_STATES.get(buttonId)
    if new_status != expected_status:
        return f"Không thể {expected_status} thiết bị {button_name}. Vui lòng thử lại."
    
    # Check if status actually changed
    if current_status == expected_status:
        return f"Thiết bị {button_name} đã ở trạng thái {expected_status} từ trước"
    
    return f"Thiết bị {button_name} đã được {expected_status} thành công (từ {current_status} -> {expected_status})"