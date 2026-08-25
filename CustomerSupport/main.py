from support_agent import CustomerSupportAgent

agent = CustomerSupportAgent()

while True:

    query = input("\nEnter query (exit to quit): ")

    if query.lower() == "exit":
        break

    result = agent.handle(query)

    print(result)