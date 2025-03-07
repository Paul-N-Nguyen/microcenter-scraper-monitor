
class Item:
    """
    Object representing a product listing or item.
    """
    def __init__(self, name, price, button_state, link):
        self.name = name
        self.price = price
        self.button_state = button_state
        self.link = link