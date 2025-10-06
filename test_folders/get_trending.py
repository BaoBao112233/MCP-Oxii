import requests
from datetime import datetime

def format_value(value):
    if value >= 1000000000:
        result = value/1000000000
        result_str = f"{result:.2f} B"
    elif value >= 1000000:
        result = value/1000000
        result_str = f"{result:.2f} M"
    elif value >= 1000:
        result = value/1000
        result_str = f"{result:.2f} K"
    else:
        result_str = f"{result:.2f}"
    
    return result_str

def get_trending_tokens(time_period: str = '6h'):
    """
    Fetch data from Axiom API using the exact headers and cookies from the curl command
    Args:
        time_period: Time period for trending data (1h, 6h, 24h)
    Returns:
        API response as formatted string or "No data" if failed

    """
    url = f'https://api.geckoterminal.com/api/v2/networks/base/trending_pools?include=base_token&page=1&duration={time_period}'

    try:
        
        response = requests.get(url)
        # Check response status
        if response.status_code == 200:
            data = response.json()['data']
            # print(data)
            if not data: return "No data"

            output_header = "Top Trending Token:\n"
            output_text = ""
            for idx, token in enumerate(data,1):
                token_address = token['attributes']['address']
                name = token['attributes']['name']
                pool_created_at = token['attributes']['pool_created_at']
                date_created = datetime.strptime(pool_created_at, "%Y-%m-%dT%H:%M:%SZ")
                fdv_usd = token['attributes']['fdv_usd']
                fdv = format_value(float(fdv_usd))

                output_text+= f"Token {idx}: Token Addess: {token_address} - Name: {name} - Created at: {date_created} - FDV: {fdv}\n"
                
            return output_header+output_text if output_text else "No data"
        else:
            print(f"Error: Status code {response.status_code}")
            # print(f"Response: {response.text}")
            return "No data"
    except Exception as e:
        print(f"Exception: {str(e)}")
        return "No data"


if __name__ == "__main__":
    results = get_trending_tokens()
    print(results)