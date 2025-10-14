"""Room-level one-touch control tool for OXII MCP server."""
from typing import Annotated

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
    """[MOCK] Execute one-touch commands for a specific room."""
    
    valid_codes = {
        "TURN_ON_ALL_DEVICES": "Đã bật tất cả thiết bị trong phòng",
        "TURN_OFF_ALL_DEVICES": "Đã tắt tất cả thiết bị trong phòng",
        "TURN_ON_LIGHT": "Đã bật đèn trong phòng",
        "TURN_OFF_LIGHT": "Đã tắt đèn trong phòng",
        "TURN_ON_FAN": "Đã bật quạt trong phòng",
        "TURN_OFF_FAN": "Đã tắt quạt trong phòng",
        "TURN_ON_HOT_COLD_SHOWER": "Đã bật máy nước nóng lạnh trong phòng",
        "TURN_OFF_HOT_COLD_SHOWER": "Đã tắt máy nước nóng lạnh trong phòng",
    }
    
    if one_touch_code not in valid_codes:
        return (
            f"Mã one-touch không hợp lệ: {one_touch_code}. Các mã hợp lệ: "
            f"{', '.join(sorted(valid_codes))}"
        )
    
    print(f"[MOCK] Room {room_id} one-touch: {one_touch_code}")
    
    # Find room and update states
    room_found = None
    for room in MOCK_ROOMS:
        if str(room.get("room_id")) == str(room_id):
            room_found = room
            break
    
    if room_found:
        # Determine action and device type
        is_on = "ON" in one_touch_code
        status = "bật" if is_on else "tắt"
        
        if "ALL_DEVICES" in one_touch_code:
            device_filter = None
        elif "LIGHT" in one_touch_code:
            device_filter = "LIGHT"
        elif "FAN" in one_touch_code:
            device_filter = "FAN"
        elif "HOT_COLD_SHOWER" in one_touch_code:
            device_filter = "HOT_COLD_SHOWER"
        else:
            device_filter = None
        
        # Update button states
        for button in room_found.get("buttons", []):
            if device_filter is None or button.get("button_type") == device_filter:
                button_id = button.get("buttonId")
                if button_id in BUTTON_STATES:
                    BUTTON_STATES[button_id] = status
    
    time.sleep(0.5)
    
    return valid_codes[one_touch_code]
