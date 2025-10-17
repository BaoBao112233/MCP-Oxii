"""Mock data storage for OXII MCP server."""

MOCK_TOKEN = "mock_token_abc123xyz"

MOCK_ROOMS = [
    {
        "house_id": 1,
        "room_id": 101,
        "room_name": "Phòng khách",
        "devices": [
            {
                "name": "Switch SH4",
                "seriNumber": "SN001",
                "device_status": "Đang kết nối"
            }
        ],
        "buttons": [
            {
                "buttonId": 1001,
                "name": "Quạt điện",
                "button_code": "0101",
                "button_type": "FAN",
                "label": "FAN",
                "modelName": "Switch-4",
                "remoteIRId": None,
                "brandId": None,
                "status": "tắt",
                "deviceId": 201,
                "seriNumber": "SN001",
                "joinMesh": 1,
                "net_Index": 1,
                "app_Index": 1
            },
            {
                "buttonId": 1002,
                "name": "Điều hòa",
                "button_code": "0102",
                "button_type": "CONDITIONER",
                "label": "CONDITIONER",
                "modelName": "Daikin",
                "remoteIRId": 301,
                "brandId": 10,
                "status": "tắt",
                "deviceId": 201,
                "seriNumber": "SN001",
                "joinMesh": 1,
                "net_Index": 1,
                "app_Index": 1
            },
            # {
            #     "buttonId": 1003,
            #     "name": "Bình nóng lạnh",
            #     "button_code": "0103",
            #     "button_type": "HOT_COLD_SHOWER",
            #     "label": "HOT_COLD_SHOWER",
            #     "modelName": "Switch-4",
            #     "remoteIRId": None,
            #     "brandId": None,
            #     "status": "tắt",
            #     "deviceId": 201,
            #     "seriNumber": "SN001",
            #     "joinMesh": 1,
            #     "net_Index": 1,
            #     "app_Index": 1
            # },
            # {
            #     "buttonId": 1004,
            #     "name": "Công tắc đèn",
            #     "button_code": "0104",
            #     "button_type": "LIGHT",
            #     "label": "LIGHT",
            #     "modelName": "Switch-4",
            #     "remoteIRId": None,
            #     "brandId": None,
            #     "status": "tắt",
            #     "deviceId": 201,
            #     "seriNumber": "SN001",
            #     "joinMesh": 1,
            #     "net_Index": 1,
            #     "app_Index": 1
            # },
            # {
            #     "buttonId": 1005,
            #     "name": "Ổ cắm",
            #     "button_code": "0105",
            #     "button_type": "SOCKET",
            #     "label": "SOCKET",
            #     "modelName": "Switch-4",
            #     "remoteIRId": None,
            #     "brandId": None,
            #     "status": "tắt",
            #     "deviceId": 201,
            #     "seriNumber": "SN001",
            #     "joinMesh": 1,
            #     "net_Index": 1,
            #     "app_Index": 1
            # },
            # {
            #     "buttonId": 1006,
            #     "name": "Bếp điện",
            #     "button_code": "0106",
            #     "button_type": "SOCKET",
            #     "label": "SOCKET",
            #     "modelName": "Switch-4",
            #     "remoteIRId": None,
            #     "brandId": None,
            #     "status": "tắt",
            #     "deviceId": 201,
            #     "seriNumber": "SN001",
            #     "joinMesh": 1,
            #     "net_Index": 1,
            #     "app_Index": 1
            # },
            # {
            #     "buttonId": 1007,
            #     "name": "Khóa cửa",
            #     "button_code": "0107",
            #     "button_type": "LOCK",
            #     "label": "LOCK",
            #     "modelName": "Smart-Lock-01",
            #     "remoteIRId": None,
            #     "brandId": None,
            #     "status": "khóa",
            #     "deviceId": 201,
            #     "seriNumber": "SN001",
            #     "joinMesh": 1,
            #     "net_Index": 1,
            #     "app_Index": 1
            # }
        ]
    }
]

MOCK_DEVICE_PROPERTIES = {
    201: {
        "id": 201,
        "seriNumber": "SN001",
        "status": 1,
        "joinMesh": 1,
        "hardwareVersion": "2",
        "properties": [
            {
                "code": "f_cronjob_setting",
                "value": '{"sch": []}'
            }
        ]
    },
    202: {
        "id": 202,
        "seriNumber": "SN002",
        "status": 1,
        "joinMesh": 1,
        "hardwareVersion": "4",
        "properties": [
            {
                "code": "ble_mesh_f_cronjob",
                "value": '[]'
            }
        ]
    }
}

# Button state storage (simulates device state changes)
BUTTON_STATES = {
    1001: "tắt",
    1002: "tắt",
    1003: "tắt",
    1004: "tắt",
    1005: "tắt"
}