class Scout:
    def __init__(self, values):
        self.values = list(values)

    def cleanup(self):
        cleaned = [self._normalize(label) for label in self.values]
        cleaned = [label for label in cleaned if label]
        return self._unique_preserving(cleaned)

    def _normalize(self, value):
        if value is None:
            return ""
        return str(value).strip().lower()

    def _unique_preserving(self, values):
        uniq = []
        seen = set()
        for value in values:
            if value in seen:
                continue
            uniq.append(value)
            seen.add(value)
        return uniq
