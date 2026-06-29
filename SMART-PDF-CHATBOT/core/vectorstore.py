import os
import json
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from langchain_classic.storage import LocalFileStore
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class VectorStoreManager:
    def __init__(self, embedding_model, index_name="new-database"):
        self.pc = Pinecone()
        self.index_name = index_name

        if self.index_name not in self.pc.list_indexes().names():
            logger.info(f"Creating new Pinecone index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=768,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )

        self.vector_store = PineconeVectorStore(
            index_name=self.index_name,
            embedding=embedding_model
        )
        os.makedirs("./docstore", exist_ok=True)
        self.store = LocalFileStore("./docstore")
        self.id_key = "doc_id"

    @staticmethod
    def sanitize_metadata(metadata: dict) -> dict:
        """
        Forces metadata to comply with Pinecone's strict schema:
        No None types, and lists must contain only strings.
        """
        sanitized = {}
        for key, value in metadata.items():
            if value is None:
                continue  # Skip None entirely
            elif isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            elif isinstance(value, list) and all(isinstance(i, str) for i in value):
                sanitized[key] = value  # Only homogenous string lists allowed
            elif isinstance(value, dict):
                sanitized[key] = json.dumps(value)  # Flatten dicts
            else:
                sanitized[key] = str(value)  # Cast anything else to string safely
        return sanitized