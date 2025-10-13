"""Cronjob scheduling tool for OXII MCP server."""
from __future__ import annotations

import json
from typing import Annotated, Dict, List

from pydantic import Field

from .common import get_device_properties, get_rooms_with_devices, _request


def _cron_to_custom_format(cron_expr: str) -> Dict[str, List[int]]:
    parts = cron_expr.strip().split()
    if len(parts) != 6:
        raise ValueError(
            "Định dạng cron không hợp lệ. Vui lòng sử dụng 6 trường: giây phút giờ ngày tháng thứ."
        )

    _, minute, hour, day, month, weekday = parts

    if day.isdigit() and month.isdigit() and weekday in {"?", "*"}:
        j = [int(day), int(month), int(hour), int(minute)]
        w: List[int] = []
    elif weekday not in {"?", "*"}:
        j = [0, 0, 0 if hour == "*" else int(hour), 0 if minute == "*" else int(minute)]
        if "," in weekday:
            w = [int(wd) for wd in weekday.split(",")]
        elif "-" in weekday:
            start, end = map(int, weekday.split("-"))
            w = list(range(start, end + 1))
        else:
            w = [int(weekday)]
    else:
        j = [0, 0, 0 if hour == "*" else int(hour), 0 if minute == "*" else int(minute)]
        w = [0, 1, 2, 3, 4, 5, 6]

    return {"j": j, "w": w}


def _find_button(token: str, button_id: int) -> Dict:
    rooms = get_rooms_with_devices(token)
    for room in rooms:
        for button in room.get("buttons", []):
            if button.get("buttonId") == button_id:
                return button
    raise ValueError(f"Không tìm thấy thông tin của nút bấm với buttonId: {button_id}")


def create_device_cronjob(
    token: Annotated[str, Field(description="Authentication token from OXII API")],
    buttonId: Annotated[int, Field(description="ID của nút cần đặt lịch")],
    cron_time: Annotated[str, Field(description="Biểu thức cron 6 trường, ví dụ: '0 30 8 * * 1-5'")],
    command: Annotated[str, Field(description="Lệnh: 'on' hoặc 'off'")],
    action: Annotated[int, Field(description="1 = tạo/cập nhật, 3 = xóa", default=1)],
    job_status: Annotated[int, Field(description="Trạng thái job: 0 = tắt, 1 = bật", default=1)],
    issetting_online: Annotated[bool, Field(description="Áp dụng ngay trên thiết bị", default=True)],
) -> str:
    """Create or update a cronjob for the specified switch button."""

    command_upper = command.strip().upper()
    if command_upper not in {"ON", "OFF"}:
        return "Lệnh không hợp lệ. Vui lòng chọn 'on' hoặc 'off'."

    try:
        button = _find_button(token, buttonId)
    except Exception as exc:  # pragma: no cover
        return str(exc)

    device_id = button.get("deviceId")
    if device_id is None:
        return "Không tìm thấy thiết bị tương ứng với nút bấm này."

    try:
        device = get_device_properties(token, int(device_id))
    except Exception as exc:  # pragma: no cover
        return f"Không thể lấy thông tin thiết bị: {exc}"

    serial_number = device.get("seriNumber")
    properties = device.get("properties", [])
    version = device.get("hardwareVersion")

    if not serial_number or not properties:
        return "Thiếu thông tin thiết bị để tạo lịch hẹn giờ."

    try:
        cron_struct = _cron_to_custom_format(cron_time)
    except ValueError as exc:
        return str(exc)

    lid = int(str(button.get("button_code", ""))[-1])
    command_flag = 1 if command_upper == "ON" else 0

    try:
        if version != "4":
            result = _create_cronjob_sh1_sh2(
                token,
                serial_number,
                properties,
                lid,
                cron_time,
                command_flag,
                job_status,
            )
        else:
            result = _create_cronjob_sh4(
            token,
            int(device_id),
            properties,
            cron_struct,
            lid,
            command_flag,
            action,
            job_status,
            issetting_online,
        )
    except Exception as exc:  # pragma: no cover
        return f"Không thể tạo lịch hẹn giờ: {exc}"

    button_name = button.get("name") or "thiết bị"
    command_text = "bật" if command_upper == "ON" else "tắt"
    return (
        f"{result} Thiết bị {button_name} sẽ được {command_text} theo lịch {cron_time}."
    )


def _create_cronjob_sh1_sh2(
    token: str,
    serial_number: str,
    properties: List[Dict],
    lid: int,
    cron_time: str,
    command_flag: int,
    job_status: int,
) -> str:
    cron_setting = next(
        (prop for prop in properties if prop.get("code") == "f_cronjob_setting"),
        None,
    )
    if not cron_setting:
        return "Thiết bị chưa hỗ trợ cấu hình cronjob."

    cron_data = json.loads(cron_setting.get("value", "{}")) or {"sch": []}
    schedule = cron_data.setdefault("sch", [])
    schedule.append(
        {
            "e": job_status,
            "j": cron_time,
            "d": [{"lid": lid, "d": command_flag}],
        }
    )

    payload = {
        "serial_number": serial_number,
        "command_type": 209,
        "data": {
            "total": len(schedule),
            "sch": schedule,
        },
    }

    _request(
        "POST",
        "/api/app/device/switch/save-crontab",
        token=token,
        json=payload,
    )

    return "Cronjob đã được tạo thành công cho thiết bị." 


def _create_cronjob_sh4(
    token: str,
    device_id: int,
    properties: List[Dict],
    cron_struct: Dict[str, List[int]],
    lid: int,
    command_flag: int,
    action: int,
    job_status: int,
    issetting_online: bool,
) -> str:
    cron_setting = next(
        (prop for prop in properties if prop.get("code") == "ble_mesh_f_cronjob"),
        None,
    )
    cronjobs = json.loads(cron_setting.get("value", "[]")) if cron_setting else []

    command_status = ["0"] * 4
    command_data = ["0"] * 4
    command_status[lid - 1] = "1"
    command_data[lid - 1] = str(command_flag)
    button_state = int("".join(command_status + command_data[::-1]), 2)

    if action == 1:
        slot = next((i for i in range(1, 11) if i not in [item.get("i") for item in cronjobs]), None)
        if slot is None:
            return "Không còn slot cronjob trống trên thiết bị."

        cron_job_data = {
            "i": slot,
            "a": action,
            "s": {"e": job_status, "j": cron_struct["j"], "w": cron_struct["w"]},
            "b": button_state,
        }
    else:
        return "Thiết bị SH4 hiện chỉ hỗ trợ thêm cronjob (action=1)."

    payload = {
        "cronJobData": cron_job_data,
        "isSettingOnl": issetting_online,
    }

    _request(
        "POST",
        f"/api/app/oxii/device/{device_id}/cronjob",
        token=token,
        json=payload,
    )

    return "Cronjob đã được tạo thành công cho thiết bị."