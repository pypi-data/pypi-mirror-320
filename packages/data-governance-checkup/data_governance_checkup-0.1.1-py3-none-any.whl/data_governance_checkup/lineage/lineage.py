class DataLineage:
    def __init__(self):
        self.tracker = []

    def add_event(self, event):
        self.tracker.append(event)

    def get_lineage(self):
        return self.tracker
