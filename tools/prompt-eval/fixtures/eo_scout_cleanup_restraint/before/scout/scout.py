class Scout:
    def __init__(self, values):
        self.values = values

    def cleanup(self):
        cleaned = []
        for item in self.values:
            if item is None:
                continue
            value = str(item).strip()
            if value:
                cleaned.append(value)
        self.values = cleaned
        return cleaned
