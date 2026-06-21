from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from pydantic import BaseModel
class BillingTicketResponse(BaseModel):
    sentiment: str
    account_id: str
    drafted_email: str
class BillingDepartment:
    def __init__(self,chat_model):
        self.chat_model=chat_model
        parser = StrOutputParser()
        prompt0 = ChatPromptTemplate.from_messages([
            ("system",
             "You are an expert analyzer. CRITICAL INSTRUCTION: Return ONLY ONE WORD representing the sentiment (e.g., Angry, Frustrated, Neutral, Happy, Anxious)."),
            ("human", "{email}")
        ])
        sentiment_chain = prompt0 | self.chat_model | parser
        prompt1 = ChatPromptTemplate.from_messages([
            ("system","""read the email and extract ONLY the account number or username. 
                      CRITICAL INSTRUCTION: Return ONLY the ID, with no conversational text."""),
            ("human","{email}")
        ])
        extraction_chain = prompt1 | self.chat_model | parser
        prompt2 = ChatPromptTemplate.from_messages([
            ('system',"You are a polite, professional billing support agent."),
            ("human", """Draft an email explaining the 3-5 business day refund policy for account: {account_id}. 

                    Here is the customer's original email for context: 
                    {email}""")
        ])
        drafting_chain=prompt2|self.chat_model|parser
        step_1_extraction = RunnableParallel({
            "email": lambda x: x["email"],
            "sentiment": sentiment_chain,
            "account_id": extraction_chain
        })
        step_2_drafting = RunnableParallel({
            "sentiment": lambda x: x["sentiment"],
            "account_id": lambda x: x["account_id"],
            "drafted_email": drafting_chain
        })

        self.chain = step_1_extraction | step_2_drafting

    def process_ticket(self, email: str):
        raw_dict = self.chain.invoke({'email': email})
        return BillingTicketResponse(**raw_dict)

