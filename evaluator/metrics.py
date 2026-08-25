class Metrics:

    def __init__(self):

        self.total_requests = 0
        self.approved = 0
        self.rejected = 0
        self.escalated = 0

    def report(self):

        print("\n===== METRICS =====")

        print(
            f"Requests: {self.total_requests}"
        )

        print(
            f"Approved: {self.approved}"
        )

        print(
            f"Rejected: {self.rejected}"
        )

        print(
            f"Escalated: {self.escalated}"
        )