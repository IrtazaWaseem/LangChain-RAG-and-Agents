from langchain_classic.retrievers.multi_vector import MultiVectorRetriever
from langchain_classic.storage._lc_store import create_kv_docstore
class AdvancedRetriever:
    def __init__(self, vectorstore, docstore):
        self.vectorstore = vectorstore
        self.docstore = docstore

    def get_retriever(self, namespace: str, k: int = 30):
        kv_store = create_kv_docstore(self.docstore)

        retriever = MultiVectorRetriever(
            vectorstore=self.vectorstore,
            docstore=kv_store,
            id_key="doc_id",
            search_kwargs={"k": k, "namespace": namespace}
        )
        return retriever