"""Room-level one-touch control tool for OXII MCP server."""
from typing import Annotated, List, Dict

from pydantic import Field

from .common import _request

from .mockup_data import MOCK_ROOMS, BUTTON_STATES
import time

def room_one_touch_control(
    token: Annotated[str, Field(description="Authentication token từ OXII API")],
    room_id: Annotated[str, Field(description="ID của phòng cần điều khiển")],
    one_touch_code: Annotated[
        str,
        Field(
            description=(
                "Mã one-touch: TURN_ON_ALL_DEVICES, TURN_OFF_ALL_DEVICES, TURN_ON_LIGHT, "
                "TURN_OFF_LIGHT, TURN_ON_FAN, TURN_OFF_FAN, TURN_ON_HOT_COLD_SHOWER, TURN_OFF_HOT_COLD_SHOWER"
            )
        ),
    ],
) -> str:
    """
    Description: [MOCK] Execute one-touch commands for a specific room.

    Args:
        token (str): Authentication token from OXII API.
        room_id (str): ID of the room to control.
        one_touch_code (str): One-touch code: TURN_ON_ALL_DEVICES, TURN_OFF_ALL_DEVICES, TURN_ON_LIGHT,
            TURN_OFF_LIGHT, TURN_ON_FAN, TURN_OFF_FAN, TURN_ON_HOT_COLD_SHOWER, TURN_OFF_HOT_COLD_SHOWER
    
    Returns:
        str: Result message of the room one-touch control action.
    """
    
    valid_codes = {
        "TURN_ON_ALL_DEVICES": ("bật", None, "tất cả thiết bị"),
        "TURN_OFF_ALL_DEVICES": ("tắt", None, "tất cả thiết bị"),
        "TURN_ON_LIGHT": ("bật", "LIGHT", "đèn"),
        "TURN_OFF_LIGHT": ("tắt", "LIGHT", "đèn"),
        "TURN_ON_FAN": ("bật", "FAN", "quạt"),
        "TURN_OFF_FAN": ("tắt", "FAN", "quạt"),
        "TURN_ON_HOT_COLD_SHOWER": ("bật", "HOT_COLD_SHOWER", "máy nước nóng lạnh"),
        "TURN_OFF_HOT_COLD_SHOWER": ("tắt", "HOT_COLD_SHOWER", "máy nước nóng lạnh"),
    }
    
    if one_touch_code not in valid_codes:
        return (
            f"Mã one-touch không hợp lệ: {one_touch_code}. Các mã hợp lệ: "
            f"{', '.join(sorted(valid_codes))}"
        )
    
    expected_status, device_filter, device_name = valid_codes[one_touch_code]
    
    print(f"[MOCK] Room {room_id} one-touch: {one_touch_code}")
    
    # Find room
    room_found = None
    for room in MOCK_ROOMS:
        if str(room.get("room_id")) == str(room_id):
            room_found = room
            break
    
    if not room_found:
        return f"Không tìm thấy phòng với ID: {room_id}"
    
    # Find matching buttons and store initial states
    matching_buttons: List[Dict] = []
    for button in room_found.get("buttons", []):
        if device_filter is None or button.get("button_type") == device_filter:
            button_id = button.get("buttonId")
            if button_id in BUTTON_STATES:
                matching_buttons.append({
                    "id": button_id,
                    "name": button.get("name"),
                    "old_status": BUTTON_STATES[button_id]
                })
    
    if not matching_buttons:
        return f"Không tìm thấy {device_name} nào trong phòng này"
    
    # Update button states
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
    room_name = room_found.get("room_name", f"phòng {room_id}")
    
    if failed_count > 0:
        return f"Có lỗi xảy ra: {failed_count}/{total} {device_name} trong {room_name} không thể {expected_status}"
    
    if unchanged_count == total:
        return f"Tất cả {device_name} trong {room_name} ({total} thiết bị) đã ở trạng thái {expected_status} từ trước"
    
    result_parts = [f"Đã {expected_status} {device_name} trong {room_name}:"]
    if changed_count > 0:
        result_parts.append(f"{changed_count} thiết bị đã được {expected_status} thành công")
    if unchanged_count > 0:
        result_parts.append(f"{unchanged_count} thiết bị đã {expected_status} từ trước")
    
    return " ".join(result_parts)