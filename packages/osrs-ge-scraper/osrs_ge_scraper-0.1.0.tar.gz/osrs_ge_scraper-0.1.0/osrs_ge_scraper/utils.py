def format_price(price):
    if isinstance(price, str) and 'k' in price:
        return int(float(price.replace('k', '')) * 1_000)
    elif isinstance(price, str) and 'm' in price:
        return int(float(price.replace('m', '')) * 1_000_000)
    elif isinstance(price, str):
        return int(price.replace(',', ''))
    return price
