import json

def search_kb(query):

    with open("kb.json") as f:
        data = json.load(f)

    for item in data:

        if item["question"].lower() in query.lower():

            return item["answer"]

    return None