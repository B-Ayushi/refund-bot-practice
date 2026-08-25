from agents.shopping_agent import (
    ShoppingAgent
)

from tools.memory_tool import (
    Memory
)

from guardrails.input_guardrails import (
    validate_input
)

from guardrails.output_guardrails import (
    validate_output
)

from evaluator.metrics import (
    Metrics
)

from tools.handoff_tool import (
    request_handoff
)

agent = ShoppingAgent()

memory = Memory()

metrics = Metrics()


while True:

    query = input(
        "\nSearch Query: "
    ).strip()

    if query.lower() == "exit":

        break

    if not validate_input(
        query
    ):

        print(
            "Blocked by guardrail"
        )

        continue

    history = memory.get_history()

    intent, response, normalized_query = agent.interpret(
        query,
        history
    )

    memory.add_message(
        "user",
        query
    )

    if intent == "handoff":

        response = request_handoff(
            memory,
            query
        )

        memory.add_message(
            "assistant",
            response
        )

        print(
            response
        )

        continue

    if intent != "shopping":

        memory.add_message(
            "assistant",
            response
        )

        print(
            response
        )

        continue

    metrics.total_queries += 1

    memory.add_message(
        "assistant",
        f"Normalized shopping request: {normalized_query}"
    )

    results = agent.recommend(
        normalized_query
    )

    if not validate_output(
        results
    ):

        print(
            "Output validation failed"
        )

        continue

    if not results:

        print(
            agent.no_results_message(
                normalized_query
            )
        )

        continue

    print(
        "\nTop Recommendations:\n"
    )

    for product in results:

        print(
            f"{product['name']} | ₹{product['price']} | "
            f"{product['shipping_days']} day shipping"
        )

metrics.report()