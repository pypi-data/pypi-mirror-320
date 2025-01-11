import requests
from .item import Item

class GrandExchangeAPI:
    BASE_URL = "https://services.runescape.com/m=itemdb_oldschool/api/catalogue/detail.json?item="

    @staticmethod
    def fetch_item_data(item_id):
        response = requests.get(f"{GrandExchangeAPI.BASE_URL}{item_id}")
        response.raise_for_status()
        data = response.json()
        return data['item']

    @classmethod
    def get_item(cls, item_id):
        item_data = cls.fetch_item_data(item_id)
        return Item(
            id=item_data['id'],
            name=item_data['name'],
            description=item_data['description'],
            current_price=item_data['current']['price'],
            today_price=item_data['today']['price'],
            members=item_data['members']
        )
