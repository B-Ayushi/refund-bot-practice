from tools.order_tools import issue_refund


class ExecutionAgent:

    def execute(self, order):

        return issue_refund(order)