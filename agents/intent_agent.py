import json
import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


class IntentAgent:

    def classify(self, query):

        prompt = f"""
Classify the user's intent.

Valid intents:

refund
refund_status
human
unknown

Return ONLY JSON.

Examples:

User: refund my order
Output:
{{"intent":"refund"}}

User: mera paisa wapas karo
Output:
{{"intent":"refund"}}

User: connect me to support
Output:
{{"intent":"human"}}

User: what's my refund status
Output:
{{"intent":"refund_status"}}

User:
{query}
"""

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        try:
            return json.loads(content)["intent"]
        except Exception:
            return "unknown"