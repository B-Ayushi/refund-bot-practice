import json


def get_fraud_score(customer_id):

    with open("data/customers.json", "r") as f:
        customers = json.load(f)

    for customer in customers:
        if customer["customer_id"] == customer_id:
            return customer["fraud_score"]

    return 0