import uuid
from typing import List, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class DocumentSplitter:
    def __init__(self, parent_chunk_size=2000, child_chunk_size=400):
        self.parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=parent_chunk_size,
            chunk_overlap=200
        )
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=child_chunk_size,
            chunk_overlap=50
        )

    def split_documents(self, documents: List[Document]) -> Tuple[List[Document], List[Document]]:
        all_parents = []
        all_children = []

        parent_docs = self.parent_splitter.split_documents(documents)

        for parent_doc in parent_docs:
            parent_id = str(uuid.uuid4())
            parent_doc.metadata["doc_id"] = parent_id
            all_parents.append(parent_doc)

            children = self.child_splitter.split_documents([parent_doc])
            for child in children:
                child.metadata = child.metadata.copy()
                child.metadata["doc_id"] = parent_id
                all_children.append(child)

        return all_parents, all_children