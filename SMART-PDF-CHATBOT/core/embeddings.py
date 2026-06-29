from langchain_ollama import OllamaEmbeddings
from langchain_core.embeddings import Embeddings

class EmbeddingsProvider:
    def __init__(self, model_name: str = "nomic-embed-text"):
        self.model_name = model_name
    def get_embeddings(self) -> Embeddings:
        embeddings = OllamaEmbeddings(model=self.model_name)
        return embeddings