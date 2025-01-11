from osrs_ge_scraper import GrandExchangeAPI

def test_fetch_item_data():
    item_data = GrandExchangeAPI.fetch_item_data(4151)
    assert item_data['id'] == 4151
