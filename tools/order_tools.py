import json


ORDERS_FILE = "data/orders.json"


def load_orders():

    with open(ORDERS_FILE, "r") as f:
        return json.load(f)


def save_orders(orders):

    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=4)


def get_order_details(order_id):

    orders = load_orders()

    for order in orders:

        if order["order_id"] == order_id:
            return order

    return None


def get_refund_status(order_id):

    order = get_order_details(order_id)

    if not order:

        return {
            "status": "order_not_found"
        }

    return {
        "order_id": order_id,
        "refund_status": order["refund_status"]
    }


def issue_refund(order):

    orders = load_orders()

    for o in orders:

        if o["order_id"] == order["order_id"]:

            o["refund_status"] = "completed"

            save_orders(orders)

            break

    return {
        "status": "approved",
        "refund_amount": order["amount"]
    }