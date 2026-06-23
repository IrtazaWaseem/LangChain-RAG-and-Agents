import os
import pandas as pd
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent
load_dotenv()


class PCAdvisorAgent:
    def __init__(self, sql_conn):
        self.sql_conn = sql_conn
        self.llm = ChatGoogleGenerativeAI(model="models/gemini-3.1-flash-lite", temperature=0.2)

        self.tools = self._setup_tools()
        self.agent_executor = self._build_agent()

    def _setup_tools(self):
        def get_game_requirements(game_title: str) -> str:
            try:
                query = "SELECT * FROM GAMES WHERE TITLE LIKE :title"
                df = pd.read_sql(query, con=self.sql_conn, params={"title": f"%{game_title}%"})

                if df.empty:
                    return f"Game '{game_title}' not found in the database."
                return f"Requirements found for {game_title}: {df.to_dict(orient='records')[0]}"
            except Exception as e:
                return f"Database error: {str(e)}"

        return [
            Tool(
                name="GameRequirementsDB",
                func=get_game_requirements,
                description="Use this to look up the minimum and recommended system requirements for a specific PC game."
            )
        ]

    def _build_agent(self):

        return create_react_agent(self.llm, self.tools)

    def chat(self, user_input: str, user_specs: str = "Unknown") -> str:

            system_instruction = (
                "You are a highly technical PC building expert and hardware analyst. "
                f"The user's current PC specifications are: {user_specs}. "
                "Use the provided tools to answer questions about hardware and game requirements. "
                "ALWAYS compare the user's specs against the game requirements if they ask if they can run a game."
            )

            try:
                response = self.agent_executor.invoke({
                    "messages": [
                        ("system", system_instruction),
                        ("user", user_input)
                    ]
                })
                return response["messages"][-1].content
            except Exception as e:
                return f"I encountered a cognitive error while processing that request: {str(e)}"
