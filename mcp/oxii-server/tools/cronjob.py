"""Cronjob scheduling tool for OXII MCP server."""
from __future__ import annotations

import json
from typing import Annotated, Dict, List

from pydantic import Field

from .common import get_device_properties, get_rooms_with_devices, _request

from .mockup_data import MOCK_ROOMS, BUTTON_STATES
import time 

def create_device_cronjob(
    token: Annotated[str, Field(description="Authentication token from OXII API")],
    buttonId: Annotated[int, Field(description="ID của nút cần đặt lịch")],
    cron_time: Annotated[str, Field(description="Biểu thức cron 6 trường, ví dụ: '0 30 8 * * 1-5'")],
    command: Annotated[str, Field(description="Lệnh: 'on' hoặc 'off'")],
    action: Annotated[int, Field(description="1 = tạo/cập nhật, 3 = xóa", default=1)],
    job_status: Annotated[int, Field(description="Trạng thái job: 0 = tắt, 1 = bật", default=1)],
    issetting_online: Annotated[bool, Field(description="Áp dụng ngay trên thiết bị", default=True)],
) -> str:
    """
    Description: [MOCK] Create or update a cronjob for the specified switch button.
    
    Args:
        token (str): Authentication token from OXII API.
        buttonId (int): ID of the button to set the cronjob for.
        cron_time (str): 6-field cron expression, e.g., '0 30 8 * * 1-5'.
        command (str): Command to execute: 'on' or 'off'.
        action (int): 1 = create/update, 3 = delete.
        job_status (int): Job status: 0 = disabled, 1 = enabled.
        issetting_online (bool): Apply immediately on device.
    
    Returns:
        str: Result message of the cronjob creation action.
    """

    command_upper = command.strip().upper()
    if command_upper not in {"ON", "OFF"}:
        return "Lệnh không hợp lệ. Vui lòng chọn 'on' hoặc 'off'."
    
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
    
    command_text = "bật" if command_upper == "ON" else "tắt"
    button_name = button_found.get("name") or "thiết bị"
    
    print(f"[MOCK] Creating cronjob for {button_name}: {cron_time} -> {command_text}")
    
    return (
        f"Cronjob đã được tạo thành công cho thiết bị. "
        f"Thiết bị {button_name} sẽ được {command_text} theo lịch {cron_time}."
    )
