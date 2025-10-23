"""Air conditioner control tool for OXII MCP server."""
from typing import Annotated

from pydantic import Field

from .common import get_rooms_with_devices, _request


def control_air_conditioner(
    power: Annotated[str, Field(description="Status power: '1'/'on' turn on, '0'/'off' turn off")],
    mode: Annotated[str, Field(description="Mode: '1'=auto, '2'=heat, '3'=cool, '4'=dry, '5'=fan", default="1")],
    temp: Annotated[str, Field(description="Target temperature (16-32)", default="24")],
    fan_speed: Annotated[str, Field(description="Fan speed: '0'=auto, '1'=low, '2'=medium, '3'=high, '4'=turbo", default="0")],
    swing_h: Annotated[str, Field(description="Horizontal swing: '1'=on, '0'=off", default="0")],
    swing_v: Annotated[str, Field(description="Vertical swing: '1'=on, '0'=off", default="0")],
) -> str:
    """
    Description: [MOCK] Send a BLE mesh command to control an OXII air conditioner.
    
    Args:
        power (str): Status power: '1'/'on' turn on, '0'/'off' turn off.
        mode (str): Mode: '1'=auto, '2'=heat, '3'=cool, '4'=dry, '5'=fan.
        temp (str): Target temperature (16-32).
        fan_speed (str): Fan speed: '0'=auto, '1'=low, '2'=medium, '3'=high, '4'=turbo.
        swing_h (str): Horizontal swing: '1'=on, '0'=off.
        swing_v (str): Vertical swing: '1'=on, '0'=off.
    
    Returns:
        str: Result message of the AC control action.
    """
    
    mode_names = {
        "1": "tự động",
        "2": "sưởi",
        "3": "làm lạnh",
        "4": "hút ẩm",
        "5": "quạt"
    }
    
    power_text = "bật" if power in ["1", "on"] else "tắt"
    mode_text = mode_names.get(mode, "tự động")
    
    print(f"[MOCK] AC Control: Power={power_text}, Mode={mode_text}, Temp={temp}°C")
    
    return (
        f"Đã gửi lệnh điều khiển điều hòa thành công "
        f"(nguồn: {power_text}, chế độ: {mode_text}, nhiệt độ: {temp}°C)."
    )