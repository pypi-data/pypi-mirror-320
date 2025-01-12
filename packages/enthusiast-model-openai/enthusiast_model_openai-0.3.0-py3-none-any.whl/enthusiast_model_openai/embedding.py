from openai import OpenAI

from enthusiast_common import EmbeddingProvider


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self):
        super(EmbeddingProvider, self).__init__()
        self._client = OpenAI()

    def generate_embeddings(self, content: str) -> list[float]:
        """
        Generates and returns an embedding vector for the given content using OpenAI's embeddings API.

        Args:
            content (str): The input text for which the embedding vector is to be generated.
        """
        openai_embedding = self._client.embeddings.create(model=self._model,
                                                          dimensions=self._dimensions,
                                                          input=content)

        return openai_embedding.data[0].embedding

    @staticmethod
    def available_models() -> list[str]:
        all_models = OpenAI().models.list().data
        return [model.id for model in all_models if model.id.startswith("text-embedding")]