"""Room-level one-touch control tool for OXII MCP server."""
from typing import Annotated

from pydantic import Field

from .common import _request


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
    """Execute one-touch commands for a specific room."""

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

    try:
        _request(
            "POST",
            f"/api/app/room/{room_id}/one-touch/{one_touch_code}/execute",
            token=token,
        )
    except Exception as exc:  # pragma: no cover
        return f"Không thể điều khiển one-touch cho phòng: {exc}"

    return valid_codes[one_touch_code]