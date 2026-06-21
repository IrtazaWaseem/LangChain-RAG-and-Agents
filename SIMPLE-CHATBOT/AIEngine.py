from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
class AIEngine:
    def __init__(self, model_name="phi3"):
        self.llm = ChatOllama(model=model_name)
        self.output_parser = StrOutputParser()

    def get_response_stream(self, persona, user_input):
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a {persona}. Answer naturally in character."),
            ("user", "{input_text}")
        ])
        chain = prompt_template | self.llm | self.output_parser
        return chain.stream({"persona": persona, "input_text": user_input})