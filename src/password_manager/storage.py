class JsonStorage:

    def load(self) -> dict:
        ...

    def persist(self, data: dict) -> None:
        ...