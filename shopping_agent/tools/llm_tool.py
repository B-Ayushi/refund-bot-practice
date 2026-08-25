import json
import os
from pathlib import Path
import urllib.error
import urllib.request


DEFAULT_OTHER_RESPONSE = (
    "I could not find a shopping request in that query. "
    "Try asking for a product, style, budget, or shipping preference."
)

DEFAULT_GREETING_RESPONSE = (
    "Hey, I am your shopping assistant. "
    "Tell me, how can I help?"
)

DEFAULT_DELIVERY_RESPONSE = (
    "I can help with delivery timing, but the current catalog does not "
    "include destination coverage. Please tell me the product and delivery "
    "location so I can check what is available."
)

DEFAULT_HANDOFF_RESPONSE = (
    "I can request help from a human shopping specialist. "
    "Please wait while your request is prepared for handoff."
)


DEFAULT_SYSTEM_PROMPT = """
You are the conversational router for a shopping assistant.
Classify the user's message as exactly one of: greeting, shopping, delivery,
handoff, other.
A greeting includes casual variations, misspellings, repeated letters,
punctuation, and short social messages. Treat 'hi', 'hiiii', 'hello!!',
'heyy', 'heyyy', and 'heyluuu' as greetings. A shopping message asks for
products, styles, prices, budgets, or specific delivery constraints. A
delivery message asks whether delivery is possible in a country or region,
or asks a general delivery question such as delivery to Europe or England.
 A handoff message asks to speak to, contact, or be connected with a human,
agent, representative, or customer support person. Treat phrases such as
'get me in touch with a human', 'I want a real person', and 'HITL' as handoff.
Do not invent destination coverage that is not provided. Everything else is
other.
Return only valid JSON with this shape:
{"intent": "greeting|shopping|delivery|handoff|other", "response": "short response", "normalized_query": "corrected user query"}
Use the conversation history to resolve follow-up references and omitted
details. For example, if the user first asks for a linen dress and then asks
whether it can be delivered to England, carry the linen dress into the
delivery interpretation. If the product or destination is already clear from
the history, use it directly in the response and do not ask the user to
repeat or confirm it. For greeting,
response should say you are the shopping assistant and ask how
you can help. For shopping, response must be an empty string and
normalized_query must correct spelling and preserve every product, budget,
style, exclusion, and delivery constraint. For other, response should
politely ask the user to describe what they want to shop for. For delivery,
answer the delivery question helpfully using only the available catalog facts;
if destination coverage is unknown, say so clearly and ask for the product and
location needed to check it. For handoff, confirm that a human handoff has
been requested; do not claim that a human has already joined the conversation.
""".strip()


def load_project_env():

    env_path = Path(__file__).resolve().parents[1] / ".env"

    if not env_path.exists():

        return

    for line in env_path.read_text().splitlines():

        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:

            continue

        key, value = line.split("=", 1)
        value = value.strip().strip("\"'")

        os.environ.setdefault(
            key.strip(),
            value
        )


load_project_env()


def classify_query(
    query,
    history=None
):

    groq_api_key = os.getenv("GROQ_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    api_key = groq_api_key or openai_api_key

    if not api_key:

        return "other", DEFAULT_OTHER_RESPONSE, query

    default_base_url = (
        "https://api.groq.com/openai/v1/chat/completions"
        if groq_api_key
        else "https://api.openai.com/v1/chat/completions"
    )

    messages = [
        {
            "role": "system",
            "content": DEFAULT_SYSTEM_PROMPT
        }
    ]

    if history:

        messages.extend(
            history[-10:]
        )

    messages.append(
        {
            "role": "user",
            "content": query
        }
    )

    request_body = json.dumps(
        {
            "model": os.getenv(
                "GROQ_MODEL",
                os.getenv("OPENAI_MODEL", "openai/gpt-oss-120b")
            ),
            "temperature": 0,
            "response_format": {
                "type": "json_object"
            },
            "messages": messages
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        os.getenv(
            "LLM_BASE_URL",
            default_base_url
        ),
        data=request_body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "shopping-agent/1.0"
        },
        method="POST"
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=10
        ) as response:

            payload = json.loads(
                response.read().decode("utf-8")
            )

        result = json.loads(
            payload["choices"][0]["message"]["content"]
        )

        intent = result.get(
            "intent",
            result.get("category")
        )
        response_text = result.get("response", "").strip()
        normalized_query = result.get(
            "normalized_query",
            query
        ).strip()

        if not normalized_query:

            normalized_query = query

        if intent not in {
            "greeting",
            "shopping",
            "delivery",
            "handoff",
            "other"
        }:

            return "other", DEFAULT_OTHER_RESPONSE, query

        if intent == "shopping":

            return intent, "", normalized_query

        if intent == "greeting" and not response_text:

            return intent, DEFAULT_GREETING_RESPONSE, normalized_query

        if intent == "delivery" and not response_text:

            return intent, DEFAULT_DELIVERY_RESPONSE, normalized_query

        if intent == "handoff" and not response_text:

            return intent, DEFAULT_HANDOFF_RESPONSE, normalized_query

        if not response_text:

            return "other", DEFAULT_OTHER_RESPONSE, query

        return intent, response_text, normalized_query

    except (
        OSError,
        ValueError,
        KeyError,
        IndexError,
        urllib.error.URLError
    ):

        return "other", DEFAULT_OTHER_RESPONSE, query
