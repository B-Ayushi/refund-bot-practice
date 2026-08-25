import re

def parse_query(query):

    query = query.lower()

    result = {
        "max_price": None,
        "max_shipping_days": None,
        "max_shipping_hours": None
    }

    price_match = re.search(
        r'under\s+(\d+)',
        query
    )

    if price_match:

        result["max_price"] = int(
            price_match.group(1)
        )

    hours_match = re.search(
        r'(?:within|withing|in|under)\s+(\d+)\s+hours?',
        query
    )

    if hours_match:

        result["max_shipping_hours"] = int(
            hours_match.group(1)
        )

    if result["max_shipping_hours"] is not None:

        return result

    if "one day" in query:

        result["max_shipping_days"] = 1

    elif "2 day" in query:

        result["max_shipping_days"] = 2

    return result