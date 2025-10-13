"""Authentication helper tool for OXII MCP server."""
import requests
from template.configs.environment import env
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_oxii_token(phone: str, password: str, country: str = "VI") -> str:
    """Return an authentication token from the OXII API."""

    try:
        response = requests.post(
            f"{env.BASE_URL}/api/app/user/signin",
            json={"phone": phone, "password": password, "country": country},
        ).json()

        if response.get("code") == 200:
            return response.get("data", {}).get("token", "")
        message = response.get("message") or "Authentication failed"
        return f"{message}"

    except Exception as exc:  # pragma: no cover - surfaced to agent
        import traceback
        traceback.print_exc()
        print(f"Authentication error: {exc}")
        return None
    
if __name__ == "__main__":
    print("OXII Smart Home Authentication Tool")
    print("=" * 40)
    phone = env.USER_PHONE
    password = env.USER_PASSWORD
    country = env.USER_COUNTRY

    token = get_oxii_token(phone, password, country)
    if token and not token.startswith("Authentication"):
        print(f"✅ Authentication successful!")
        print(f"Token preview: {token[:20]}...")
    else:
        print(f"❌ Authentication failed: {token}")