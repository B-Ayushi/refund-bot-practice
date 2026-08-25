from data.products import PRODUCTS


def search_products(
    constraints
):

    results = []

    for product in PRODUCTS:

        if (
            constraints["max_price"]
            is not None
        ):

            if product["price"] > constraints["max_price"]:

                continue

        if (
            constraints["max_shipping_days"]
            is not None
        ):

            if (
                product["shipping_days"]
                >
                constraints["max_shipping_days"]
            ):

                continue

        if (
            constraints["max_shipping_hours"]
            is not None
        ):

            if (
                product["shipping_days"] * 24
                >
                constraints["max_shipping_hours"]
            ):

                continue

        results.append(product)

    return results