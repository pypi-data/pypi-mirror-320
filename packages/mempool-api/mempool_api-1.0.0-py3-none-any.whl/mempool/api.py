import requests

class Mempool:
    def __init__(self, base_url: str = "https://mempool.space/api/"):
        # initialize the instance with the base URL for the API
        self._base_url = base_url

    def _url_fetcher(self, endpoint: str) -> dict:
        # fetch data from a given endpoint and return the JSON response as a dictionary
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            # print the error if the request fails and return None
            print(f"Error fetching {endpoint}: {e}")
            return None

    def get_btc_price(self, currency: str) -> float:
        # get the current BTC price in the specified currency
        if not isinstance(currency, str):
            print("Invalid currency type.")
            return 0.0
        price = self._url_fetcher(f"{self._base_url}v1/prices")
        if price:
            return float(price.get(currency.upper(), 0.0))
        return 0.0

    def get_btc_address_balance(self, address: str) -> float:
        # get the balance of a given BTC address
        if not isinstance(address, str):
            print("Invalid address type.")
            return 0.0
        balance = self._url_fetcher(f"{self._base_url}address/{address}")
        if balance and 'chain_stats' in balance:
            return float(balance['chain_stats']['funded_txo_sum'] / 100000000)
        print("Could not fetch address balance")
        return 0.0

    def btc_address_validation(self, address: str) -> bool:
        # validate if the given BTC address is valid
        if not isinstance(address, str):
            print("Invalid address type.")
            return False
        validation = self._url_fetcher(f"{self._base_url}v1/validate-address/{address}")
        return bool(validation and validation.get('isvalid'))

    def get_last_btc_block_height(self) -> int:
        # get the height of the last BTC block
        block_info = self._url_fetcher(f"{self._base_url}blocks/tip/height")
        return int(block_info) if block_info else None

    def get_active_btc_pools(self) -> list[dict]:
        # get the list of active BTC mining pools
        pools_info = self._url_fetcher(f"{self._base_url}v1/mining/pools/1w")
        return pools_info.get('pools', []) if pools_info else []

    def get_btc_fees(self) -> tuple:
        # get the recommended BTC transaction fees
        fees_info = self._url_fetcher(f"{self._base_url}v1/fees/recommended")
        if fees_info:
            fastest = fees_info.get('fastestFee', 0)
            economy = fees_info.get('economyFee', 0)
            minimum = fees_info.get('minimumFee', 0)
            return int(fastest), int(economy), int(minimum)
        return 0, 0, 0