from config import REFUND_WINDOW_DAYS


class PolicyAgent:

    def check(self, order):

        if order["refund_status"] == "completed":

            return (
                False,
                "already_refunded"
            )

        if order["status"] != "Delivered":

            return (
                False,
                "not_delivered"
            )

        if order["days_since_delivery"] > REFUND_WINDOW_DAYS:

            return (
                False,
                "refund_window_expired"
            )

        if order["product_type"] == "Digital":

            return (
                False,
                "digital_product"
            )

        return (
            True,
            "eligible"
        )