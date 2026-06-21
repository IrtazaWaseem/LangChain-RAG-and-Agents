from pydantic import BaseModel,Field
from typing import Literal
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

class TicketCategory(BaseModel):
    department:Literal["Billing","Technical","General"]=Field(description="Department of the ticket")

class TicketClassifier:
    def __init__(self,chat_model):
        self.chat_model=chat_model
        self.parser = PydanticOutputParser(pydantic_object=TicketCategory)
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert email routing AI. Read the user's email and classify it into the correct department.
                   CRITICAL INSTRUCTION: You must respond ONLY with valid JSON. Do not include any conversational text.{format_instructions}"""),
            ("human", "{email}")
        ])

        self.chain = prompt | self.chat_model | self.parser
    def categorize(self,email):
        result = self.chain.invoke({'email': email,'format_instructions': self.parser.get_format_instructions()})
        return result
