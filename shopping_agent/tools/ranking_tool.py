def rank_products(
    products,
    query
):

    query = query.lower()

    for product in products:

        score = 0

        for tag in product["tags"]:

            if tag in query:

                score += 1

        product["score"] = score

    return sorted(
        products,
        key=lambda x: x["score"],
        reverse=True
    )