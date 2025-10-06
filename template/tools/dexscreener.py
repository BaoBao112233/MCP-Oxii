import requests
import datetime
from typing import Annotated
from pydantic import Field

def convert_info_to_string(info):
    """
    Chuyển đổi thông tin dự án thành chuỗi.
    
    Args:
        info (dict): Thông tin dự án.
        
    Returns:
        str: Chuỗi thông tin dự án.
    """
    try:
        # Lấy dữ liệu cơ bản
        symbol = info["baseToken"]["symbol"]
        name = info["baseToken"]["name"]
        chain = info["chainId"]
        contract_address = info["baseToken"]["address"]
        try:
            price = float(info["priceUsd"])
        except Exception as e:
            print(f"Lỗi khi chuyển đổi giá thành số: {e}")
            import traceback
            traceback.print_exc()
            price = 0.0
        
        # Tính tuổi của token
        current_time = datetime.datetime.now()
        pair_created_timestamp = info["pairCreatedAt"] / 1000  # Chuyển đổi từ milliseconds sang seconds
        pair_created_time = datetime.datetime.fromtimestamp(pair_created_timestamp)
        time_diff = current_time - pair_created_time
        
        hours_diff = int(time_diff.total_seconds() / 3600)
        days_diff = int(hours_diff / 24)
        
        if days_diff > 0:
            age_text = f"{days_diff} days"
        else:
            age_text = f"{hours_diff} hours"
        
        # Lấy thông tin về giá trị thị trường và phần trăm thay đổi
        marketcap = info["marketCap"] 
        if marketcap >= 1000000000:
            marketcap = f"{marketcap/1000000000}B"
        elif marketcap >= 1000000 and marketcap < 1000000000:
            marketcap = f"{marketcap/1000000}M"
        elif marketcap >= 1000 and marketcap < 1000000:
            marketcap = f"{marketcap/1000}K"
        percent_change_1h = "1h: "+str(info["priceChange"].get("h1", "N/A")) +"%"
        percent_change_24h = "24h:" + str(info["priceChange"].get("h24", "N/A")) +"%"
        
        # Thông tin về thanh khoản (LP)
        lp_value_usd = info["liquidity"]["usd"]
        if lp_value_usd >= 1000000000:
            lp_value_usd = f"{lp_value_usd/1000000000}B"
        elif lp_value_usd >= 1000000:
            lp_value_usd = f"{lp_value_usd/1000000}M"
        elif lp_value_usd >= 1000:
            lp_value_usd = f"{lp_value_usd/1000}K"
        lp_value_base = info["liquidity"]["base"]
        lp_value_quote = info["liquidity"]["quote"]
        

        # print("symbol :", symbol, type(symbol))
        # print("name :", name, type(name))   
        # print("chain :", chain, type(chain))
        # print("contract address:", contract_address, type(contract_address))
        # print("price :", price, type(price))
        # print("marketcap :", marketcap, type(marketcap))
        # print("percent_change_1h :", percent_change_1h, type(percent_change_1h))
        # print("percent_change_24h :", percent_change_24h, type(percent_change_24h))
        # print("age_text :", age_text, type(age_text))
        # print("lp_value_usd :", lp_value_usd, type(lp_value_usd))
        # print("lp_value_base :", lp_value_base, type(lp_value_base))
        # print("lp_value_quote :", lp_value_quote, type(lp_value_quote))
        # Chuyển đổi giá trị thành chuỗi với định dạng mong muốn



        # Tạo chuỗi kết quả theo định dạng yêu cầu
        result = f"""
    Token AI Analyze 
    ${symbol}
    Name: {name} 
    Chain: {chain}
    Renounced: CA: {contract_address} 
    Price of token: ${price}
    Token Info:
    Marketcap: {marketcap}
    {percent_change_1h} | {percent_change_24h}
    Age: {age_text}
    LP Info:
    - LP Value: {lp_value_quote} {info["quoteToken"]["symbol"]} / {lp_value_base} {symbol} (${lp_value_usd})
    """
        return result
    except Exception as e:
        print(f"Lỗi khi chuyển đổi thông tin dự án thành chuỗi: {e}")
        import traceback
        traceback.print_exc()
        return None
    
def convert_bundles_to_string(bundles_data, top_bundles=3):
    """
    Chuyển đổi danh sách bundles thành chuỗi.
    
    Args:
        bundles_data (dict): Dictionary chứa thông tin về bundles.
        top_bundles (int): Số lượng bundle hàng đầu để hiển thị.
        
    Returns:
        str: Chuỗi danh sách bundles.
    """

    try:
        # Check if bundles_data is a dictionary
        if not isinstance(bundles_data, dict):
            raise TypeError("Expected a dictionary for bundles_data, but received a different type")
            
        total_bundles = bundles_data['total_bundles']
        # Chuyển đổi sang đơn vị triệu (M) hoặc nghìn (K) tùy thuộc vào giá trị
        total_tokens_value = bundles_data['total_tokens_bundled']
        
        if total_tokens_value >= 1000000000:
            total_tokens_bundled = f"{total_tokens_value/1000000000:.2f}B"
        elif total_tokens_value >= 1000000:
            total_tokens_bundled = f"{total_tokens_value/1000000:.2f}M"
        elif total_tokens_value >= 1000:
            total_tokens_bundled = f"{total_tokens_value/1000:.2f}K"
        else:
            total_tokens_bundled = total_tokens_value
        total_percentage_bundled = bundles_data['total_percentage_bundled']
        total_base_spent = bundles_data['total_base_spent']
        holding_percentage = bundles_data['creator_analysis']['holding_percentage']
        bonded = "Yes" if bundles_data['bonded'] else "No"
        
        total_coins_created = bundles_data['creator_analysis']['history']['total_coins_created']
        current_holdings = bundles_data['creator_analysis']['current_holdings']

        result = f"""
    Advanced Bundle Analysis
    Overall Statistics
    Total Bundles: {total_bundles}
    Total Tokens Bundled: {total_tokens_bundled}
    Total Percentage Bundled: {total_percentage_bundled:.2f}%
    Total BASE Spent: {total_base_spent:.2f} BASE
    Current Held Percentage: {holding_percentage:.2f}%
    Bonded: {bonded}

    Creator Risk Profile
    Total Created: {total_coins_created} 
    Current Token Held: {current_holdings}

    Top {top_bundles} Bundles:
    """

        json_bundles = bundles_data['bundles']
        list_bundles = []
        for bundles_id, bundle_data in json_bundles.items():
            bundle = {
                "slot": bundles_id,
                "unique_wallets": bundle_data["unique_wallets"],
                "primary_category": bundle_data['bundle_analysis']["primary_category"],
                "total_tokens": bundle_data["total_tokens"],
                "total_percentage": bundle_data["token_percentage"],
                "total_base_spent": bundle_data["total_base"],
                "holding_amount": bundle_data["holding_amount"],
                "holding_percentage": bundle_data["holding_percentage"],
            }
            list_bundles.append(bundle)
            
        # Sort bundles by percentage in descending order
        list_bundles.sort(key=lambda x: x["total_percentage"], reverse=True)

        for bundle in list_bundles[:top_bundles]:
            total_token = bundle["total_tokens"]
            if total_token >= 1000000000:
                total_token = f"{total_token/1000000000:.2f}B"
            elif total_token >= 1000000:
                total_token = f"{total_token/1000000:.2f}M"
            elif total_token >= 1000:
                total_token = f"{total_token/1000:.2f}K"
            tmp = f"""
    Slot: {bundle['slot']}
    Unique Wallets: {bundle['unique_wallets']}
    Primary Category: {bundle['primary_category']}
    Tokens Bought: {total_token}
    % of Supply: {bundle['total_percentage']:.2f}%
    base Spent: {bundle['total_base_spent']:.2f} base
    Holding Amount: {bundle['holding_amount']}
    Holding Percentage: {bundle['holding_percentage']:.2f}%
    """
            result += tmp
        result += "\n"
        return result
    except Exception as e:
        print(f"Lỗi khi chuyển đổi danh sách bundles thành chuỗi: {e}")
        import traceback
        traceback.print_exc()
        return None

def convert_bubble_map_to_string(nodes, top_nodes=3):
    """
    Chuyển đổi danh sách bubble thành chuỗi.
    
    Args:
        nodes (list): Danh sách bubble.
        
    Returns:
        str: Chuỗi danh sách casc nodes.
    """

    try:
        # Chuyển đổi danh sách KOLs thành chuỗi
        length_nodes = len(nodes)
        list_nodes = nodes[:top_nodes]

        result = f"""
Bubble Map Mentions: {length_nodes}
"""     
        if length_nodes == 0:
            return result
        
        result += f"Top {top_nodes} Bubble Map:\n"

        for node in list_nodes:
            tmp = f"Address: {node['address']} ({node['percentage']:.2f}%)\n"
            result += tmp
        result += "\n"
        return result
    except Exception as e:
        print(f"Lỗi khi chuyển đổi danh sách KOLs thành chuỗi: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_contract_address_from_pairID(
    pair_id: Annotated[str, Field(description="The unique identifier of the token pair")]
) -> str:
    """
    Lấy thông tin về một cặp giao dịch từ Dexscreener API
    
    Args:
        pair_id (str): ID của cặp giao dịch trên base
        
    Returns:
        dict: Dữ liệu về cặp giao dịch hoặc None nếu có lỗi
    """
    url = f"https://api.dexscreener.com/latest/dex/pairs/base/{pair_id}"
    
    print("Get contract address from pair ID")
    try:
        # Gửi GET request đến API với timeout 10 giây
        response = requests.get(url, timeout=10)
        
        # Kiểm tra status code
        if response.status_code == 200:
            # Parse response thành JSON
            data = response.json()
            
            # Trường hợp 1: pair là null
            if data.get('pair') is None:
                print("Trường hợp 1: pair là null")
                contract_address = pair_id
                return contract_address
            
            # Trường hợp 2: pair có dữ liệu
            pair = data['pair']
            print(pair)
            
            if 'baseToken' in pair and 'address' in pair['baseToken']:
                contract_address = pair['baseToken']['address']
                return contract_address
            else:
                # Nếu không tìm thấy baseToken hoặc address, trả về pair_id
                print("Không tìm thấy baseToken hoặc address trong pair")
                return pair_id
        else:
            print(f"Lỗi: API trả về status code {response.status_code}")
            return None
    except requests.exceptions.Timeout:
        print("Lỗi: Yêu cầu API đã hết thời gian chờ (timeout)")
        return None
    except Exception as e:
        print(f"Đã xảy ra lỗi khi gọi API: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    
def get_contract_address_from_ticker(
    ticker: Annotated[str, Field(description="The ticker symbol of the cryptocurrency or token")]
) -> str:
    """
    Lấy thông tin về một cặp giao dịch từ Dexscreener API
    
    Args:
        pair_id (str): ID của cặp giao dịch trên base
        
    Returns:
        dict: Dữ liệu về cặp giao dịch hoặc None nếu có lỗi
    """
    url = f"https://api.dexscreener.com/latest/dex/search?q={ticker}"
    
    print("Get contract address from ticker")
    try:
        # Gửi GET request đến API
        response = requests.get(url, timeout=10)
        
        # Kiểm tra status code
        if response.status_code == 200:
            # Parse response thành JSON
            data = response.json()

            contract_address = "No have contract address!"

            list_pair = data['pairs']
            for pair in list_pair:
                if pair['chainId'] == 'base':
                    contract_address = pair['baseToken']['address']
                    break

            return contract_address
        else:
            print(f"Lỗi: API trả về status code {response.status_code}")
            return None
    except Exception as e:
        print(f"Đã xảy ra lỗi khi gọi API: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def get_info_token(
    contract_address: Annotated[str, Field(description="The contract address of the token")]
) -> str:
    """
    Lấy thông tin về một cặp giao dịch từ Dexscreener API
    
    Args:
        pair_id (str): ID của cặp giao dịch trên base
        
    Returns:
        dict: Dữ liệu về cặp giao dịch hoặc None nếu có lỗi
    """
    url = f"https://api.dexscreener.com/latest/dex/tokens/{contract_address}"
    print("Get Information token")
    try:
        # Gửi GET request đến API
        response = requests.get(url, timeout=10)
        
        # Kiểm tra status code
        if response.status_code == 200:
            # Parse response thành JSON
            data = response.json()

            list_pair = data.get('pairs', [])
            
            if not list_pair:
                return "No have infor about this token!"
            
            for pair in list_pair:
                if pair['chainId'] == 'base':
                    info = convert_info_to_string(pair)
                    print(f"info: {info}")
                    return info
    
            return "No have infor about this token!"
        else:
            print(f"Lỗi: API trả về status code {response.status_code}")
            return None
    except Exception as e:
        print(f"Đã xảy ra lỗi khi gọi API: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    
def get_bundle_token(
    contract_address: Annotated[str, Field(description="The contract address of the token bundle")]
) -> str:
    """
    Lấy thông tin về bundle
    
    Args:
        contract_address (str): Địa chỉ contract của token trên base
        
    Returns:
        dict: Dữ liệu về bundle hoặc thông báo nếu có lỗi
    """
    url = f"https://trench.bot/api/bundle/bundle_advanced/{contract_address}"
    print("Get Bundle token")
    try:
        # Gửi GET request đến API với timeout 10 giây
        response = requests.get(url, timeout=10)
        
        # Kiểm tra status code
        if response.status_code == 200:
            # Parse response thành JSON
            data = response.json()
            
            # Trường hợp 2: Kiểm tra nếu response chứa error
            if isinstance(data, dict) and "error" in data:
                print(f"Lỗi từ API: {data['error']}")
                return "No have bundle about this token!"
            
            # Trường hợp 1: Xử lý dữ liệu bình thường
            bundles = convert_bundles_to_string(data)
            print(f"bundles: {bundles}")
            return bundles if bundles else "No have infor about this token!"
        else:
            print(f"Lỗi: API trả về status code {response.status_code}")
            return "No have bundle about this token!"
    except requests.exceptions.Timeout:
        print("Lỗi: Yêu cầu API đã hết thời gian chờ (timeout)")
        return "No have bundle about this token!"
    except Exception as e:
        print(f"Đã xảy ra lỗi khi gọi API: {str(e)}")
        import traceback
        traceback.print_exc()
        return "No have bundle about this token!"

def get_bubble_map_token(
    contract_address: Annotated[str, Field(description="The contract address of the token for the bubble map")]
) -> str:
    """
    Lấy thông tin bubble map token từ API.
    
    Args:
        contract_address (str): Địa chỉ hợp đồng của token.
        
    Returns:
        dict: Dữ liệu bubble map token được trả về từ API.
        None: Nếu có lỗi xảy ra.
    """
    url = f"https://europe-west1-cryptos-tools.cloudfunctions.net/get-bubble-graph-data?token={contract_address}&chain=base"
    print("Get Bubble map token")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Kiểm tra lỗi HTTP
        
        data = response.json()
        
        # Trường hợp 2: Xử lý khi trả về lỗi xác thực với status KO
        if isinstance(data, dict) and "status" in data and data["status"] == "KO":
            return "No have bubble map about this token!"
        
        # Trường hợp 1: Kiểm tra xem response có chứa lỗi không (cách cũ)
        if isinstance(data, dict) and "error" in data:
            return "No have bubble map about this token!"
        
        # Kiểm tra xem response có chứa dữ liệu không
        if not isinstance(data, dict) or "nodes" not in data:
            return "No have bubble map about this token!"
            
        # Lấy danh sách nodes từ dữ liệu
        nodes = data["nodes"]
        # Kiểm tra xem nodes có dữ liệu không
        if not nodes:
            return "No have bubble map about this token!"
            
        # Lưu dữ liệu vào file nếu được yêu cầu
        result = convert_bubble_map_to_string(nodes)
        print(f"result: {result}")
        return result
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gọi API: {e}")
        import traceback
        traceback.print_exc()
        return None


# if __name__ == "__main__":
#     # Test the functions
#     # pair_id = "0x123456789abcdef"
#     # contract_address = get_contract_address_from_pairID(pair_id)
#     # print(f"Contract address from pair ID: {contract_address}")

#     # ticker = "base-USDC"
#     # contract_address = get_contract_address_from_ticker(ticker)
#     # print(f"Contract address from ticker: {contract_address}")

#     ca = "8BtoThi2ZoXnF7QQK1Wjmh2JuBw9FjVvhnGMVZ2vpump"
#     # print(get_info_token(ca))

#     print(get_bundle_token(ca))