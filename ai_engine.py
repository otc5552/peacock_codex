from core.models.router import Router


class AIEngine:
    """Small compatibility wrapper for older UI modules."""

    def __init__(self, model_name=None):
        self.model_name = model_name
        self.router = Router()

    def chat(self, prompt):
        return self.router.send_message(prompt, model_name=self.model_name)

    def clear_context(self):
        return None
