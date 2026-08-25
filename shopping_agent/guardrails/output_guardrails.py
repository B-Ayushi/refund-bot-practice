def validate_output(
    results
):

    for product in results:

        if product["price"] < 0:

            return False

    return True