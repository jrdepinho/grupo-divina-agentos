from __future__ import annotations


class Context(dict):

    def remember(self, key, value):
        self[key] = value

    def recall(self, key, default=None):
        return self.get(key, default)


context = Context()
