import requests
import json
import os
from typing import Annotated
from pydantic import Field

def convert_kols_to_string(kols, top_kols=5):
    """
    Chuyển đổi danh sách KOLs thành chuỗi.
    
    Args:
        kols (list): Danh sách KOLs.
        
    Returns:
        str: Chuỗi danh sách KOLs.
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
            tmp = f"{kol['post_url'].replace(" ","")}\n"
            result += tmp
        result += "\n"
        return result
    except Exception as e:
        print(f"Lỗi khi chuyển đổi danh sách KOLs thành chuỗi: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_kols_token(
        kol_base_url: Annotated[str, Field(description="Kols token base url")],
        contract_address: Annotated[str, Field(description="Contract address")],
    ) -> str:
    """
    Lấy thông tin chi tiết về một dự án dựa trên địa chỉ ca và lưu vào file.
    
    Args:
        ca (str): Địa chỉ ca của dự án. Mặc định là "8BtoThi2ZoXnF7QQK1Wjmh2JuBw9FjVvhnGMVZ2vpump".
        save_to_file (bool): Có lưu kết quả vào file hay không. Mặc định là True.
        
    Returns:
        dict: Dữ liệu dự án được trả về từ API.
        None: Nếu có lỗi xảy ra.
    """
    url = f"{kol_base_url}/project/detail-by-ca?ca={contract_address}"
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
    Lưu dữ liệu vào file JSON trong thư mục degenlimo_result.
    
    Args:
        data (dict): Dữ liệu cần lưu
        ca (str): Địa chỉ ca, được sử dụng làm tên file
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
