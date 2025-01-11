class Item:
    def __init__(self, id, name, description, current_price, today_price, members):
        self.id = id
        self.name = name
        self.description = description
        self.current_price = current_price
        self.today_price = today_price
        self.members = members

    def __str__(self):
        return f"{self.name} (ID: {self.id}): {self.current_price} gp"

    def price_difference(self):
        return self.today_price - self.current_price

    def is_members_only(self):
        return self.members
