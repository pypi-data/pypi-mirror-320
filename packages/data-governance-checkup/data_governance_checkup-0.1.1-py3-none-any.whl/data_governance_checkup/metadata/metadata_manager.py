class MetadataManager:
    def __init__(self):
        self.metadata = {}

    def add_metadata(self, key, value):
        self.metadata[key] = value

    def get_metadata(self, key):
        return self.metadata.get(key, "Metadata not found")
