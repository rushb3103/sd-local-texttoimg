class Job:
    def __init__(self, id, prompt):
        self.id = id
        self.prompt = prompt
        self.status = "queued"
        self.progress = 0
        self.result = None
        self.error = None
