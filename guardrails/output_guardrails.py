def validate_output(response):

    if "refund_amount" in response:

        if response["refund_amount"] < 0:
            return False

    return True