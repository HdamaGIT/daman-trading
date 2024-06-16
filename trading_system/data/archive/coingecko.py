import requests

def fetch_global_market_data():
    url = "https://api.coingecko.com/api/v3/global"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

data = fetch_global_market_data()
if data:
    print("Bitcoin Dominance:", data["data"]["market_cap_percentage"]["btc"])
