import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from OmniMas import OmniMaster
from dotenv import load_dotenv
load_dotenv()

@st.cache_resource
def load_model(m1,temp):
    return ChatGoogleGenerativeAI(
        model=m1,
        temperature=temp
    )
#@st.cache_resource
def load_agent(_model1,_model2):
    return OmniMaster(_model1,_model2)

m1=load_model("models/gemini-3.1-flash-lite",0.0)
m2=load_model("models/gemini-3.1-flash-lite",0.5)
agent = load_agent(m1,m2)
st.title("OMNI-AGENT")
email = st.text_area("paste your email: ",height=200)

if st.button("Analyze Ticket"):
    if email.strip() == "":
        st.warning("Please paste an email first!")
    else:
        with st.spinner("Triaging and routing ticket"):
            result = agent.analyze_and_route(email)

            st.success("Ticket Processed")
            st.subheader("Ticket Analysis & Automation")

            if hasattr(result, 'sentiment'):
                st.text_input(
                    label="Customer Sentiment Analysis",
                    value=result.sentiment,
                    disabled=True
                )
            if hasattr(result, 'bug_report'):
                st.info("Routed to Technical Department")
                st.text_area(
                    label="Extracted Technical Issue",
                    value=result.bug_report,
                    height=150
                )
            elif hasattr(result, 'account_id'):
                st.info("Routed to Billing Department")
                st.text_input(
                    label="Extracted Account ID",
                    value=result.account_id,
                    disabled=True
                )
            if hasattr(result, 'drafted_email'):
                st.text_area(
                    label="Automated Reply Draft",
                    value=result.drafted_email,
                    height=350
                )
            if not hasattr(result, 'sentiment') and not hasattr(result, 'drafted_email'):
                st.info("Routed to Human Support")
                st.json(result)