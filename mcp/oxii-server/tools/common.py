"""Common utilities for OXII MCP server tools."""
from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional

import requests

BASE_URL = "https://stg-oxii-api.smarthiz.vn"
TIME_RETRY = 30


class OXIIError(RuntimeError):
    """Custom exception for OXII tooling errors."""


def _request(method: str, path: str, *, token: Optional[str] = None, **kwargs) -> requests.Response:
    url = f"{BASE_URL}{path}"
    headers = kwargs.pop("headers", {})
    headers.setdefault("accept", "application/json")
    headers.setdefault("Content-Type", "application/json")
    headers.setdefault("X-Origin", "smarthiz")
    if token:
        headers.setdefault("Authorization", f"Bearer {token}")

    response = requests.request(method, url, headers=headers, **kwargs)
    response.raise_for_status()
    return response


def get_home_structure(token: str) -> List[Dict[str, Any]]:
    """Return parsed device structure for the authenticated user."""
    response = _request("GET", "/api/app/oxii/home", token=token)
    payload = response.json().get("data", {})
    homes = payload.get("data", [])
    if not homes:
        raise OXIIError("Không tìm thấy thông tin nhà")
    return homes


def get_rooms_with_devices(token: str) -> List[Dict[str, Any]]:
    """Return rooms enriched with devices and remote buttons."""
    home = get_home_structure(token)[0]
    rooms = home.get("rooms", [])
    formatted_rooms: List[Dict[str, Any]] = []
    for room in rooms:
        formatted_room = {
            "house_id": home["id"],
            "room_id": room["id"],
            "room_name": room.get("name"),
            "devices": [],
            "buttons": [],
        }

        for device in room.get("devices", []):
            formatted_room["devices"].append(
                {
                    "name": device.get("models", {}).get("displayName"),
                    "seriNumber": device.get("seriNumber"),
                    "device_status": "Không thể kết nối"
                    if device.get("status") == 2 and device.get("joinMesh") == 0
                    else "Đang kết nối",
                }
            )

        for button in room.get("remoteButtons", []):
            mesh_control = button.get("device", {}).get("meshControl") or {}
            formatted_room["buttons"].append(
                {
                    "buttonId": button.get("id"),
                    "name": button.get("name"),
                    "button_code": button.get("code"),
                    "button_type": button.get("type"),
                    "label": button.get("label"),
                    "modelName": button.get("modelName"),
                    "remoteIRId": button.get("remoteIRId"),
                    "brandId": button.get("brandId"),
                    "status": "bật" if button.get("status") == "1" else "tắt",
                    "deviceId": button.get("device", {}).get("id"),
                    "seriNumber": button.get("device", {}).get("seriNumber"),
                    "joinMesh": button.get("joinMesh"),
                    "net_Index": mesh_control.get("net_Index"),
                    "app_Index": mesh_control.get("app_Index"),
                }
            )

        formatted_rooms.append(formatted_room)
    return formatted_rooms


def serialise_rooms(rooms: List[Dict[str, Any]]) -> str:
    return json.dumps(rooms, ensure_ascii=False, indent=4)


def wait_for_status_update(checker, timeout: int = TIME_RETRY, interval: float = 1.0) -> Optional[str]:
    start = time.time()
    while time.time() - start < timeout:
        result = checker()
        if result:
            return result
        time.sleep(interval)
    return None


def get_device_properties(token: str, device_id: int) -> Dict[str, Any]:
    response = _request("GET", f"/api/app/oxii/device/{device_id}/properties", token=token)
    return response.json().get("data", {})