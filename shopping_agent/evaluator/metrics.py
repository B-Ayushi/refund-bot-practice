class Metrics:

    def __init__(self):

        self.total_queries = 0

    def report(self):

        print(
            "\nTotal Queries:",
            self.total_queries
        )