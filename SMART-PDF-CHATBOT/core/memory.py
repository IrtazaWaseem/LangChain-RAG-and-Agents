from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import trim_messages
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
import logging

logger = logging.getLogger(__name__)


class MemoryManager:
    def __init__(self):
        self.store = {}

    def get_session_history(self, session_id: str) -> InMemoryChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = InMemoryChatMessageHistory()
        return self.store[session_id]

    def clear_session(self, session_id: str):
        if session_id in self.store:
            del self.store[session_id]

    def get_stateful_chain(self, base_chain):
        trimmer = trim_messages(
            max_tokens=2000,
            strategy="last",
            token_counter=len,
            include_system=True
        )
        trimmed_chain = RunnablePassthrough.assign(
            history=RunnableLambda(lambda x: trimmer.invoke(x["history"]))
        ) | base_chain

        resilient_chain = trimmed_chain.with_retry(
            stop_after_attempt=3,
            wait_exponential_jitter=True
        )

        stateful_chain = RunnableWithMessageHistory(
            runnable=resilient_chain,
            get_session_history=self.get_session_history,
            input_messages_key="question",
            history_messages_key="history",
        )

        return stateful_chain