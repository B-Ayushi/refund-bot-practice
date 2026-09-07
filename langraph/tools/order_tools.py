ORDERS = {
    "1001": "Delivered",
    "1002": "In Transit",
    "1003": "Processing"
}

def get_order_status(order_id):

    return ORDERS.get(order_id, "Not Found")