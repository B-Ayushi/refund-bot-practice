from intents import classify_intent
from knowledge_base import search_kb
from tools import *

class CustomerSupportAgent:

    def handle(self, query):

        intent = classify_intent(query)

        if intent == "faq":

            answer = search_kb(query)

            return {
                "intent":"faq",
                "answer":answer
            }

        if intent == "tracking":

            return get_order_status("1001")

        if intent == "cancellation":

            return cancel_order("1001")

        if intent == "escalation":

            return {
                "action":"transfer_to_human"
            }

        return {
            "action":"fallback"
        }