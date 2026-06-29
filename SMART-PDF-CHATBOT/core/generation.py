import logging
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableParallel, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
logger = logging.getLogger(__name__)

template = '''You are an expert document analyst and Knowledge Base Assistant.

1. CONTEXT PRIORITY: Always analyze the provided 'Context' first.
2. SUPPLEMENTAL KNOWLEDGE: If the context is insufficient, use your general knowledge to fill in gaps.
3. SUMMARIZATION: When asked for a summary, leverage headings and extrapolate based on those topics using your training.
4. RESTRICTIONS: Do not refer to document numbers or file metadata.

Context:
{context}

Question:
{question}

Answer:'''

rag_prompt = ChatPromptTemplate.from_template(template)

class RAGPipeline:
    def __init__(self, retriever):
        self.retriever = retriever
        self.primary_llm = ChatGoogleGenerativeAI(model="models/gemini-3.1-flash-lite", temperature=0.3)
        self.fallback_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.3)

    @staticmethod
    def _format_docs(docs: list) -> str:
        formatted_text = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get("source", "Unknown Document")
            formatted_text.append(f"[Source: {source}]\n{doc.page_content}")
        return "\n\n".join(formatted_text)

    def get_chain(self):
        extract_question = RunnableLambda(lambda x: x["question"])
        format_docs = RunnableLambda(self._format_docs)

        setup_and_retrieval = RunnableParallel(
            context=(extract_question | self.retriever | format_docs),
            # FIXED: We now specifically extract only the question string
            question=extract_question
        )

        primary_chain = (setup_and_retrieval | rag_prompt | self.primary_llm | StrOutputParser())
        fallback_chain = (setup_and_retrieval | rag_prompt | self.fallback_llm | StrOutputParser())
        return primary_chain.with_fallbacks(fallbacks=[fallback_chain])