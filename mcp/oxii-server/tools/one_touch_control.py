"""One-touch control helpers for OXII MCP server."""
from typing import Annotated, List, Dict

from pydantic import Field

from .common import get_rooms_with_devices, wait_for_status_update, _request
import time
from .mockup_data import MOCK_ROOMS, BUTTON_STATES

def one_touch_control_all_devices(
    token: Annotated[str, Field(description="Authentication token from OXII API")],
    command: Annotated[str, Field(description="Lệnh: 'on' hoặc 'off'")],
) -> str:
    """
    Description: [MOCK] Switch all devices in the home on or off.
    
    Args:
        token (str): Authentication token from OXII API.
        command (str): Command: 'on' or 'off'.
    
    Returns:
        str: Result message of the one-touch control action.
    """
    
    action = command.strip().upper()
    if action not in {"ON", "OFF"}:
        return "Lệnh one-touch không hợp lệ. Vui lòng dùng 'on' hoặc 'off'."
    
    expected_status = "bật" if action == "ON" else "tắt"
    
    print(f"[MOCK] One-touch control ALL devices -> {expected_status}")
    
    # Store initial states
    initial_states = {bid: status for bid, status in BUTTON_STATES.items()}
    
    # Update all button states
    for button_id in BUTTON_STATES:
        BUTTON_STATES[button_id] = expected_status
    
    # Simulate delay
    time.sleep(0.5)
    
    # Verify state changes
    changed_count = 0
    unchanged_count = 0
    failed_count = 0
    
    for button_id in BUTTON_STATES:
        new_status = BUTTON_STATES[button_id]
        old_status = initial_states.get(button_id)
        
        if new_status != expected_status:
            failed_count += 1
        elif old_status == expected_status:
            unchanged_count += 1
        else:
            changed_count += 1
    
    # Build result message
    if failed_count > 0:
        return f"Có lỗi xảy ra: {failed_count} thiết bị không thể {expected_status}"
    
    if unchanged_count == len(BUTTON_STATES):
        return f"Tất cả thiết bị đã ở trạng thái {expected_status} từ trước"
    
    result_parts = []
    if changed_count > 0:
        result_parts.append(f"{changed_count} thiết bị đã được {expected_status} thành công")
    if unchanged_count > 0:
        result_parts.append(f"{unchanged_count} thiết bị đã {expected_status} từ trước")
    
    return ", ".join(result_parts)


def one_touch_control_by_type(
    token: Annotated[str, Field(description="Authentication token from OXII API")],
    device_type: Annotated[
        str,
        Field(description="Loại thiết bị: LIGHT, TV, CONDITIONER, FAN, HOT_COLD_SHOWER, SOCKET"),
    ],
    action: Annotated[str, Field(description="Lệnh: 'on' hoặc 'off'")],
) -> str:
    """
    Description: [MOCK] Switch devices of a specific type on or off.
    
    Args:
        token (str): Authentication token from OXII API.
        device_type (str): Device type: LIGHT, TV, CONDITIONER, FAN, HOT_COLD_SHOWER, SOCKET.
        action (str): Command: 'on' or 'off'.
    
    Returns:
        str: Result message of the one-touch control action.
    """
    
    valid_device_types = {"LIGHT", "TV", "CONDITIONER", "FAN", "HOT_COLD_SHOWER", "SOCKET"}
    device_type_upper = device_type.strip().upper()
    
    if device_type_upper not in valid_device_types:
        return f"Loại thiết bị không hợp lệ. Các loại hợp lệ: {', '.join(sorted(valid_device_types))}"
    
    action_upper = action.strip().upper()
    if action_upper not in {"ON", "OFF"}:
        return "Hành động không hợp lệ. Các lựa chọn hợp lệ: on, off"
    
    expected_status = "bật" if action_upper == "ON" else "tắt"
    
    print(f"[MOCK] One-touch control {device_type_upper} -> {expected_status}")
    
    # Find matching devices and store initial states
    matching_buttons: List[Dict] = []
    for room in MOCK_ROOMS:
        for button in room.get("buttons", []):
            if button.get("button_type") == device_type_upper:
                button_id = button.get("buttonId")
                if button_id in BUTTON_STATES:
                    matching_buttons.append({
                        "id": button_id,
                        "name": button.get("name"),
                        "old_status": BUTTON_STATES[button_id]
                    })
    
    if not matching_buttons:
        return f"Không tìm thấy thiết bị nào có loại {device_type_upper}"
    
    # Update states
    for btn in matching_buttons:
        BUTTON_STATES[btn["id"]] = expected_status
    
    # Simulate delay
    time.sleep(0.5)
    
    # Verify state changes
    changed_count = 0
    unchanged_count = 0
    failed_count = 0
    
    for btn in matching_buttons:
        new_status = BUTTON_STATES[btn["id"]]
        
        if new_status != expected_status:
            failed_count += 1
        elif btn["old_status"] == expected_status:
            unchanged_count += 1
        else:
            changed_count += 1
    
    # Build result message
    total = len(matching_buttons)
    
    if failed_count > 0:
        return f"Có lỗi xảy ra: {failed_count}/{total} thiết bị {device_type_upper} không thể {expected_status}"
    
    if unchanged_count == total:
        return f"Tất cả thiết bị {device_type_upper} ({total} thiết bị) đã ở trạng thái {expected_status} từ trước"
    
    result_parts = []
    if changed_count > 0:
        result_parts.append(f"{changed_count} thiết bị {device_type_upper} đã được {expected_status} thành công")
    if unchanged_count > 0:
        result_parts.append(f"{unchanged_count} thiết bị đã {expected_status} từ trước")
    
    return ", ".join(result_parts)