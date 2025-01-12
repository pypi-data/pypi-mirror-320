class Storage:
    def __init__(self, filename: str):
        with open(filename, "w", encoding="utf-8") as self.storage:
            pass
