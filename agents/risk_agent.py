from config import MAX_AUTO_REFUND
from config import FRAUD_THRESHOLD

from tools.fraud_tools import get_fraud_score


class RiskAgent:

    def assess(self, order):

        if order["amount"] > MAX_AUTO_REFUND:

            return True

        fraud_score = get_fraud_score(
            order["customer_id"]
        )

        if fraud_score > FRAUD_THRESHOLD:

            return True

        return False