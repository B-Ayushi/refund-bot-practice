class Memory:

    def __init__(self):

        self.context = {}
        self.context["messages"] = []

    def add_message(
        self,
        role,
        content
    ):

        self.context["messages"].append(
            {
                "role": role,
                "content": content
            }
        )

        self.context["messages"] = self.context["messages"][-10:]

    def get_history(self):

        return list(
            self.context["messages"]
        )

    def update(
        self,
        key,
        value
    ):

        self.context[key] = value

    def get(
        self,
        key
    ):

        return self.context.get(key)

    def show(self):

        return self.context