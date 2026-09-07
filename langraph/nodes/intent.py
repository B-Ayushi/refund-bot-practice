import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from instructions_loader import load_instruction


load_dotenv(Path(__file__).resolve().parents[1] / ".env")
INTENT_INSTRUCTIONS = load_instruction("intent")


class IntentDecision(BaseModel):
    intent: Literal["refund", "cancel", "status", "faq"]


intent_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY"),
).with_structured_output(IntentDecision)


def detect_intent(state):
    query = state["user_query"].lower()
    try:
        decision = intent_llm.invoke(
            [
                SystemMessage(content=INTENT_INSTRUCTIONS),
                HumanMessage(content=query),
            ]
        )
        intent = decision.intent
    except Exception:
        if "refund" in query:
            intent = "refund"
        elif "cancel" in query:
            intent = "cancel"
        elif "where" in query or "status" in query or "track" in query:
            intent = "status"
        else:
            intent = "faq"

    return {"intent": intent}


def route_intent(state):
    return state["intent"]