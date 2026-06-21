from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from pydantic import BaseModel
class TechTicketResponse(BaseModel):
    sentiment: str
    bug_report: str
    drafted_email: str
class TechnicalDepartment:
    def __init__(self,llm):
        self.llm = llm
        parser = StrOutputParser()
        prompt1=ChatPromptTemplate.from_messages([
            ('system','You are an expert analyzer that analyzes the tone of given email'
                      'CRITICAL INSTRUCTION:Return ONLY ONE WORD representing the sentiment (e.g., Angry, Frustrated, Neutral, Happy)'),
            'human',"{email}"

        ])
        sentiment_chain = prompt1 | self.llm | parser
        prompt2=ChatPromptTemplate.from_messages([
            ('system','extract the technical issue and format it as a clean, bulleted list of "Steps to Reproduce" for following {email}'),
            ('human',"{email}")
        ])
        extraction_chain = prompt2 | self.llm | parser
        prompt3 = ChatPromptTemplate.from_messages([
            ('system',
            'write a highly technical, professional response apologizing for the bug, assuring them the engineering team is reviewing the logs, and providing a standard sign-off for following {email}'),
            ('human', "{email}")
        ])
        drafting_chain = prompt3 | self.llm | parser
        self.chain = RunnableParallel({
            "sentiment": sentiment_chain,
            "bug_report": extraction_chain,
            "drafted_email": drafting_chain
        })

    def process_ticket(self, email: str) -> TechTicketResponse:
            raw_dict = self.chain.invoke({'email': email})
            return TechTicketResponse(**raw_dict)
