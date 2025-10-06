import concurrent.futures
import datetime
import os
import time
from typing import Annotated

import requests
from pydantic import Field

from tools.twitter.twitter import PageContentGetter

absolution_path = os.path.abspath(__file__)
curls_dir = os.path.join(os.path.dirname(absolution_path), 'twitter', 'curls', 'geckoterminal')
geckoterminal_getter = PageContentGetter(curls_dir, from_json=False)


def get_pair_address_from_token_address(token_address: str):
    """
    Get pair address from token address
    """
    url = f"https://api.dexscreener.com/tokens/v1/base/{token_address}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
            return data[0]['pairAddress']
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def get_category_id(pair_address: str):
    """
    Get category ID for a token contract
    
    Args:
        contract_address (str): Contract address to query
    """
    try:
        url = f"https://app.geckoterminal.com/api/p1/base/pools/{pair_address}?include=dex%2Cdex.network.explorers%2Cdex_link_services%2Cnetwork_link_services%2Cpairs%2Ctoken_link_services%2Ctokens.token_security_metric%2Ctokens.token_social_metric%2Ctokens.tags%2Cpool_locked_liquidities&base_token=0"
        response = geckoterminal_getter.get_json(url)
        print(f"Response: {response}")
        if response:
            data = response
            tags = []
            print(f"Response: {data}")
            for item in data["included"]:
                if item["type"] == "tag" and item['attributes']['name'] != 'pump fun':
                    tags.append(item["attributes"]["name"].replace(" ", "-"))
            return tags
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def get_token_by_category_id(category_id: str, pair_address: str = None):
    """
    Get token by category ID
    
    Args:
        category_id (str): Category ID to query
        contract_address (str): Contract address to query
    """
    try:
        url = f'https://app.geckoterminal.com/api/p1/tags/{category_id}/base/pools?sort=-1h_trend_score'
        response = geckoterminal_getter.get_json(url)
        print(f"Response: {response['data']}")
        if response:
            data = response
            tokens = []
            for item in data["data"]:
                tagged_token_id = item['attributes']['tagged_token_id']
                marketcap = item['attributes']['token_value_data'][tagged_token_id]['fdv_in_usd']
                pool = {
                    'pair_address': item['attributes']['address'],
                    'token_symbol': item['attributes']['name'],
                    'marketcap': marketcap,
                    'age': item['attributes']['pool_created_at'],
                }
                tokens.append(pool)
                if len(tokens) >= 5:
                    break
            return tokens
    except Exception as e:
        print(f"Error: {e}")
        return None


# token_address = '43yfnktSfyKkPXRLyevHu8rNXwWHxTXS1ntQbeArpump'
# pair_address = get_pair_address_from_token_address(token_address)
# print(pair_address)
# tags = get_category_id(pair_address)
# print(tags)
# tokens = get_token_by_category_id(tags[0], pair_address)
# print(tokens)
# exit()


def format_number(value):
    """
    Format number to K, M, B format
    
    Args:
        value: Number to format
        
    Returns:
        str: Formatted number with appropriate suffix
    """
    try:
        value = float(value)
        if value >= 1_000_000_000:
            return f"{value/1_000_000_000:.2f}B"
        elif value >= 1_000_000:
            return f"{value/1_000_000:.2f}M"
        elif value >= 1_000:
            return f"{value/1_000:.2f}K"
        else:
            return f"{value:.2f}"
    except (ValueError, TypeError):
        return str(value)


def format_age(timestamp_ms):
    """
    Format token age from creation timestamp
    
    Args:
        timestamp_ms: Token creation timestamp in milliseconds
        
    Returns:
        str: Formatted age (days, hours or minutes)
    """
    if not timestamp_ms:
        return "Unknown"
    
    try:
        # Convert milliseconds to seconds
        timestamp_s = timestamp_ms / 1000
        
        # Calculate age in seconds
        current_time = time.time()
        age_seconds = current_time - timestamp_s
        
        # Format based on age
        if age_seconds < 0:  # Future date (shouldn't happen)
            return "Invalid date"
        elif age_seconds < 3600:  # Less than an hour
            minutes = int(age_seconds / 60)
            return f"{minutes}m"
        elif age_seconds < 86400:  # Less than a day
            hours = int(age_seconds / 3600)
            return f"{hours}h"
        elif age_seconds < 2592000:  # Less than 30 days
            days = int(age_seconds / 86400)
            return f"{days}d"
        else:  # More than 30 days
            months = int(age_seconds / 2592000)
            return f"{months}mo"
    except Exception as e:
        print(f"Error formatting age: {e}")
        return "Unknown"


def parse_age(age: str):
    """
    Format token age from string
    
    Args:
        age: age in format 2025-02-24T19:06:37.000Z
        
    Returns:
        str: Formatted age (days, hours or minutes)
    """
    try:
        # Parse ISO format timestamp to datetime
        dt = datetime.datetime.strptime(age, "%Y-%m-%dT%H:%M:%S.%fZ")
        
        # Convert to timestamp
        timestamp_ms = dt.timestamp() * 1000
        
        # Use existing format_age function
        return format_age(timestamp_ms)
        
    except Exception as e:
        print(f"Error parsing age: {e}")
        return "Unknown"


def get_similar_token_v2(
    contract_address: Annotated[str, Field(description="The contract address of the token to find similar tokens for")],
):
    """
    Get similar tokens using DexScreener API
    
    Args:
        contract_address (str): Contract address to query (token address)
        
    Returns:
        str: Similar tokens
    """
    try:
        pair_address = get_pair_address_from_token_address(contract_address)
        if pair_address is None:
            pair_address = contract_address
        print(pair_address)
        tags = get_category_id(pair_address)
        print(tags)
        tokens = get_token_by_category_id(tags[0], pair_address)
        result_parts = []
        for token in tokens:
            print(token)
            if token['pair_address'] == pair_address:
                continue
            result_parts.append(f"{token['token_symbol']} : {token['pair_address']} | Marketcap: {format_number(token['marketcap'])} | Age: {parse_age(token['age'])}")
        result_string = "\n".join(result_parts)
        print(f"Similar Token: {result_string}")
        return "Similar Token:\n" + result_string
    except Exception as e:
        print(f"Error: {e}")
        return "Similar Token:\nNo similar tokens found."
    


def get_similar_token(base_url: str, contract_address: str, include_market_info: bool = True):
    """
    Get data from TokenSuggest API and extract address and symbol of first 5 objects
    If include_market_info=True, add marketcap and liquidity information

    Args:
        base_url (str): Base URL of API
        contract_address (str): Contract address to query
        include_market_info (bool): Whether to get market information

    Returns:
        str: String containing address, symbol and market information of similar tokens
    """
    # URL endpoint của API
    url = f"{base_url}/TokenSuggest/query?token_address={contract_address}"
    
    print("Getting similar tokens")

    try:
        # Gọi API với phương thức GET
        response = requests.get(url, timeout=10)
        print(f"Response: {response.text}")
        # Kiểm tra response status
        if response.status_code == 200:
            # Chuyển JSON thành đối tượng Python
            json_data = response.json()
            top_tokens = [item for item in json_data if item.get("distance", 0) > 0.5]
            # Lấy 5 đối tượng đầu tiên (hoặc ít hơn nếu không đủ)
            top_tokens = top_tokens[:20]
            
            # Tạo danh sách token để xử lý
            tokens = []
            for item in top_tokens:
                if "entity" in item and "address" in item["entity"] and "symbol" in item["entity"]:
                    address = item["entity"]["address"]
                    symbol = item["entity"]["symbol"]
                    tokens.append({"address": address, "symbol": symbol})
            
            # Nếu có yêu cầu lấy thông tin thị trường, sử dụng xử lý song song
            if include_market_info and tokens:
                tokens = get_market_info_parallel(tokens)
            
            # Tạo chuỗi kết quả
            result_parts = []
            for token in tokens:
                if include_market_info and "market_info" in token:
                    market_info = token["market_info"]
                    # Filter by marketcap, liquidity and transaction counts
                    if (market_info.get("marketcap", 0) > 50000 and 
                        market_info.get("liquidity", 0) > 10000 and
                        (market_info.get("m5_txns", 0) > 2 or market_info.get("h1_txns", 0) > 50)):
                        
                        marketcap = format_number(market_info.get('marketcap', 0))
                        liquidity = format_number(market_info.get('liquidity', 0))
                        
                        # Format token age
                        created_at = market_info.get('created_at')
                        age = format_age(created_at) if created_at else "Unknown"
                        
                        result_parts.append(
                            f"{token['symbol']} : {token['address']} | "
                            f"Marketcap: {marketcap} | "
                            f"Liquidity: {liquidity} | "
                            f"Age: {age}"
                        )
            if len(result_parts) > 0:
                # Ghép các phần thành một chuỗi
                result_string = "\n".join(result_parts)
                print(f"Similar Token: {result_string}")
                return "Similar Token:\n" + result_string
            else:
                print("No similar tokens found")
                return "Similar Token:\nNo similar tokens found."
        else:
            print(f"Lỗi khi gọi API: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Đã xảy ra lỗi: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def get_market_info_parallel(tokens):
    """
    Get market information for multiple tokens in parallel

    Args:
        tokens (list): List of tokens to get information

    Returns:
        list: List of tokens with added market information
    """
    print(f"Fetching market info for {len(tokens)} tokens in parallel")
    
    def fetch_market_info(token):
        address = token["address"]
        market_info = get_token_market_info(address)
        token["market_info"] = market_info
        return token
    
    # Sử dụng ThreadPoolExecutor để gọi API song song
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Map các token vào hàm fetch_market_info và thu thập kết quả
        updated_tokens = list(executor.map(fetch_market_info, tokens))
    
    return updated_tokens

def get_token_market_info(contract_address: str):
    """
    Get marketcap, liquidity, transaction and age information for a token contract from DexScreener API
    
    Args:
        contract_address (str): Contract address to query
        
    Returns:
        dict: Dictionary containing token market information
    """
    url = f"https://api.dexscreener.com/latest/dex/tokens/{contract_address}"
    
    print(f"Getting market info for {contract_address}")

    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data and "pairs" in data and data["pairs"]:
                pair = data["pairs"][0]
                
                marketcap = pair.get("marketCap", 0)
                liquidity = pair.get("liquidity", {}).get("usd", 0)
                
                # Extract transaction data
                txns = pair.get("txns", {})
                m5_txns = txns.get("m5", {})
                h1_txns = txns.get("h1", {})
                
                # Calculate total transactions in periods
                m5_total = m5_txns.get("buys", 0) + m5_txns.get("sells", 0)
                h1_total = h1_txns.get("buys", 0) + h1_txns.get("sells", 0)
                
                # Get token creation timestamp
                created_at = pair.get("pairCreatedAt", None)
                
                result = {
                    "marketcap": marketcap,
                    "liquidity": liquidity,
                    "m5_txns": m5_total,
                    "h1_txns": h1_total,
                    "m5_buys": m5_txns.get("buys", 0),
                    "m5_sells": m5_txns.get("sells", 0),
                    "h1_buys": h1_txns.get("buys", 0),
                    "h1_sells": h1_txns.get("sells", 0),
                    "created_at": created_at
                }
                
                print(f"Market info: {result}")
                return result
            else:
                print("No pairs data found")
                return {"marketcap": 0, "liquidity": 0, "m5_txns": 0, "h1_txns": 0, "created_at": None}
        else:
            print(f"API error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# Ví dụ sử dụng
if __name__ == "__main__":
    # contract_address = "8x5VqbHA8D7NkD52uNuS5nnt3PwA8pLD34ymskeSo2Wn"
    contract_address = "2lqf52yuqjumvpkw2vy2hjwjpkyq3fhzcnmf9lfaqt6q"
    # contract_address = "KENJSUYLASHUMfHyy5o4Hp2FdNqZg1AsUPhfH2kYvEP"
    base_url = "http://192.168.10.5:9093"
    # base_url = "http://13.229.239.154:9093"
    result = get_similar_token_v2(base_url, contract_address)
    
    if result:
        print(result)  # In ra chuỗi kết quả
    else:
        print("Không thể lấy dữ liệu từ API")