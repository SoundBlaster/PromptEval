from .cleanup_pipeline import CleanupPipeline


class Scout:
    def __init__(self, values):
        self.values = values

    def cleanup(self):
        pipeline = CleanupPipeline(self.values)
        return pipeline.execute()
