import streamlit as st
from core.ai_agent import PCAdvisorAgent


def render_chatbot(sql_conn):
    st.markdown(
        """
        <style>
        .stChatMessage p {
            font-size: 20px !important;
            line-height: 1.5 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("PC Hardware & Game Advisor")

    if "ai_agent" not in st.session_state:
        st.session_state.ai_agent = PCAdvisorAgent(sql_conn)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant",
             "content": "Hello! I can help you check if your PC meets the requirements for any game in our registry. What are you looking to play?"}
        ]

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input := st.chat_input("Ask about game compatibility or specs..."):
        with st.chat_message("user"):
            st.markdown(user_input)

        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.chat_message("assistant"):
            with st.spinner("Analyzing requirements..."):
                if "user_rig" in st.session_state and st.session_state.user_rig.get("CPU") != "Not Assigned":
                    rig = st.session_state.user_rig
                    saved_specs = f"CPU: {rig.get('CPU')}, GPU: {rig.get('GPU')}, RAM: {rig.get('RAM')}, SSD: {rig.get('SSD')}, OS: {rig.get('OS')}"
                else:
                    saved_specs = "No custom specifications configured yet."

                raw_response = st.session_state.ai_agent.chat(user_input, user_specs=saved_specs)

                if isinstance(raw_response, list):
                    clean_response = ""
                    for block in raw_response:
                        if isinstance(block, dict) and "text" in block:
                            clean_response += block["text"]
                        elif isinstance(block, str):
                            clean_response += block
                    final_text = clean_response if clean_response else str(raw_response)
                elif isinstance(raw_response, dict) and "text" in raw_response:
                    final_text = raw_response["text"]
                else:
                    final_text = str(raw_response)

                st.markdown(final_text)

        st.session_state.chat_history.append({"role": "assistant", "content": final_text})