from enthusiast_common.interfaces import LanguageModelProvider
from langchain_core.language_models import BaseLanguageModel
from langchain_openai import ChatOpenAI
from openai import OpenAI


class OpenAILanguageModelProvider(LanguageModelProvider):
    def provide_language_model(self) -> BaseLanguageModel:
        return ChatOpenAI(name=self._model)

    @staticmethod
    def available_models() -> list[str]:
        all_models = OpenAI().models.list().data
        return [model.id for model in all_models if model.id.startswith("gpt-4")]
