from core.providers.provider_manager import ProviderManager
from core.personality.personality_manager import PersonalityManager
from core.context.context_builder import ContextBuilder
from core.agentic.memory_engine import MemoryEngine
from core.agentic.reflection_engine import ReflectionEngine
from core.validators.code_validator import CodeValidator
from core.parsers.code_parser import CodeParser


class UniversalRuntime:
    def __init__(self):
        self.provider = ProviderManager()
        self.personality = PersonalityManager()
        self.context = ContextBuilder()
        self.memory = MemoryEngine()
        self.reflection = ReflectionEngine()
        self.validator = CodeValidator()
        self.parser = CodeParser()

    def generate(self, user_input):
        self.memory.remember(user_input)
        context = self.context.build(user_input, self.memory.recall(), [])
        raw_response = self.provider.generate(context)
        response = self.personality.humanize(user_input, raw_response)
        code = self.parser.extract_code(response)
        validation = self.validator.validate_python(code)
        reflection = self.reflection.reflect(user_input, code, validation)
        
        return {
            "response": response,
            "code": code,
            "validation": validation,
            "reflection": reflection
        }