from tools.query_parser import (
    parse_query
)

from tools.search_tool import (
    search_products
)

from tools.ranking_tool import (
    rank_products
)
from data.products import PRODUCTS
from tools.llm_tool import (
    classify_query
)


class ShoppingAgent:

    def no_results_message(
        self,
        query
    ):

        constraints = parse_query(
            query
        )

        if constraints["max_shipping_hours"] is not None:

            fastest_shipping_days = min(
                product["shipping_days"]
                for product in PRODUCTS
            )

            return (
                f"I could not find anything that can be delivered within "
                f"{constraints['max_shipping_hours']} hours. "
                f"The fastest available delivery is "
                f"{fastest_shipping_days} day; please consider allowing "
                "more delivery time."
            )

        if constraints["max_price"] is not None:

            lowest_price = min(
                product["price"]
                for product in PRODUCTS
            )

            if constraints["max_price"] < lowest_price:

                return (
                    f"I could not find anything within your budget of "
                    f"₹{constraints['max_price']}. "
                    f"The most affordable item currently starts at "
                    f"₹{lowest_price}; please consider increasing your budget."
                )

        return (
            "I could not find a matching product. "
            "Try adjusting your style, budget, or shipping preference."
        )

    def interpret(
        self,
        query,
        history=None
    ):

        return classify_query(
            query,
            history
        )

    def recommend(
        self,
        query
    ):

        normalized_query = query.lower()

        searchable_terms = {
            product["category"]
            for product in PRODUCTS
        }

        for product in PRODUCTS:

            searchable_terms.update(
                product["tags"]
            )

        has_product_match = any(
            term in normalized_query
            for term in searchable_terms
        )

        has_constraint = (
            "under" in normalized_query
            or "one day" in normalized_query
            or "2 day" in normalized_query
            or "hour" in normalized_query
        )

        if not has_product_match and not has_constraint:

            return []

        constraints = parse_query(
            query
        )

        products = search_products(
            constraints
        )

        ranked = rank_products(
            products,
            query
        )

        return ranked[:3]