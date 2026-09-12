"""EduCore context and short-term conversation memory."""

from collections import deque


class ContextManager:
    def __init__(self, limit=12):
        self.history = deque(maxlen=limit)
        self.context = {}

    def update(self, values=None, message=None):
        if values:
            self.context.update({key: value for key, value in values.items() if value is not None})
        if message:
            self.history.append(message)
        return self.snapshot()

    def snapshot(self):
        return {**self.context, "conversationHistory": list(self.history)}

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})
