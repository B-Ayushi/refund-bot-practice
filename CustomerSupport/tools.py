def get_order_status(order_id):

    return {
        "order_id":order_id,
        "status":"In Transit"
    }


def cancel_order(order_id):

    return {
        "status":"Cancelled"
    }