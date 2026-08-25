class HumanReview:

    def review(self, order):

        print("\n===== HUMAN REVIEW =====")
        print(order)

        decision = input(
            "Approve refund? (yes/no): "
        )

        return decision.lower() == "yes"