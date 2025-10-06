import requests
import json
import os
from typing import Annotated
from pydantic import Field

BASE_URL = "https://api.degen.limo"

def convert_kols_to_string(kols, top_kols=5):
    """
    Convert KOLs list to string.

    Args:
        kols (list): List of KOLs.

    Returns:
        str: String of KOLs list.
    """

    try:
        # Chuyển đổi danh sách KOLs thành chuỗi
        mentions = kols["mentions_count"]
        list_kols = kols["kols"][:top_kols]

        result = f"""
    KOL Mentions: {mentions}
    Top {top_kols} KOL`s posts:
    """
        for kol in list_kols:
            tmp = f"{kol['post_url'].replace(' ','')}\n"
            result += tmp
        result += "\n"
        return result
    except Exception as e:
        print(f"Lỗi khi chuyển đổi danh sách KOLs thành chuỗi: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_kols_token(
        contract_address: Annotated[str, Field(description="Contract address")],
    ) -> str:
    """
    Get details about a project based on the ca address and save to file.

    Args:
        ca (str): The ca address of the project. Defaults to "8BtoThi2ZoXnF7QQK1Wjmh2JuBw9FjVvhnGMVZ2vpump".
        save_to_file (bool): Whether to save the results to a file. Defaults to True.

    Returns:
        dict: The project data returned from the API.
        None: If an error occurs.
    """
    url = f"{BASE_URL}/project/detail-by-ca?ca={contract_address}"
    print("Geting kols token")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Kiểm tra lỗi HTTP
        
        data = response.json()

        print(f"data: {data}")

        # Lưu dữ liệu vào file nếu được yêu cầu
        # if save_to_file and data:
        #     save_data_to_file(data, contract_address)
        
        kols = data.get("data", {})
        # Lấy thông tin KOLs
        if not kols:  # Kiểm tra nếu sentiment là từ điển rỗng
            kols = "No have data: KOLs.\n"
        else:
            kols = convert_kols_to_string(kols)

        return f"{kols}"
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gọi API: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_data_to_file(data, contract_address):
    """
    Save the data to a JSON file in the degenlimo_result folder.

    Args:
        data (dict): Data to save
        ca (str): Ca address, used as file name
    """
    # Tạo thư mục nếu chưa tồn tại
    output_dir = "degenlimo_result"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Tên file là giá trị của ca
    file_path = os.path.join(output_dir, f"{contract_address}.json")
    
    # Ghi dữ liệu vào file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Đã lưu dữ liệu vào file: {file_path}")
    except Exception as e:
        print(f"Lỗi khi lưu file: {e}")
