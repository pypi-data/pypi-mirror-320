from osrs_ge_scraper.item import Item

def test_item():
    item = Item(4151, "Abyssal Whip", "A powerful weapon", 2500000, 2400000, True)
    assert item.is_members_only() is True
    assert item.price_difference() == -100000
