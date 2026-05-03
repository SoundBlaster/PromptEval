class CleanupPipeline:
    def __init__(self, values):
        self.values = values

    def execute(self):
        normalized = [str(item).strip().lower() for item in self.values if item is not None]
        return sorted(set(normalized))
