from AIEngine import AIEngine
from DatabaseBuilder import DatabaseHandler
import streamlit as st
class ChatUI:
    def __init__(self, db_handler, ai_engine):
        self.db = db_handler
        self.ai = ai_engine
        self._setup_page()

    def _setup_page(self):
        st.set_page_config(page_title="Dynamic AI Chat", page_icon="🤖", layout="wide")
        st.title("The Enterprise Chatbot")

    def _handle_sidebar(self):
        st.sidebar.title("⚙️ Bot Settings")
        persona = st.sidebar.selectbox(
            "Choose the AI Persona:",
            ["Customer Support Agent", "Sarcastic Senior Software Engineer", "Expert Sports Commentator",
             "Explain Like I'm 5 Years Old", "Database Architect", "Advanced Programmer and Problem Solver"]
        )

        if "chat_sessions" not in st.session_state:
            saved_sessions = self.db.get_all_sessions()

            if saved_sessions:
                st.session_state.chat_sessions = {}
                for session_name in saved_sessions:
                    st.session_state.chat_sessions[session_name] = self.db.load_session_messages(session_name)

                st.session_state.active_chat = saved_sessions[-1]

                try:
                    highest_num = max([int(name.split(" ")[1]) for name in saved_sessions if name.startswith("Chat ")])
                    st.session_state.chat_counter = highest_num
                except:
                    st.session_state.chat_counter = len(saved_sessions)
            else:
                st.session_state.chat_sessions = {"Chat 1": []}
                st.session_state.active_chat = "Chat 1"
                st.session_state.chat_counter = 1

        st.sidebar.markdown("---")

        if st.sidebar.button("➕ Create New Chat", use_container_width=True):
            st.session_state.chat_counter += 1
            new_name = f"Chat {st.session_state.chat_counter}"
            st.session_state.chat_sessions[new_name] = []
            st.session_state.active_chat = new_name
            st.rerun()

        # UPDATED DELETION LOGIC HERE
        st.sidebar.markdown("### Your Chats")
        for chat_name in list(st.session_state.chat_sessions.keys()):
            col1, col2 = st.sidebar.columns([8, 2])
            is_active = (chat_name == st.session_state.active_chat)

            with col1:
                if st.button(chat_name, type="primary" if is_active else "secondary", use_container_width=True,
                             key=f"btn_{chat_name}"):
                    st.session_state.active_chat = chat_name
                    st.rerun()

            with col2:
                if st.button("🗑️", key=f"del_{chat_name}", help="Delete this chat"):
                    self.db.delete_session(chat_name)
                    del st.session_state.chat_sessions[chat_name]

                    if is_active:
                        if st.session_state.chat_sessions:
                            st.session_state.active_chat = list(st.session_state.chat_sessions.keys())[-1]
                        else:
                            st.session_state.chat_sessions = {"Chat 1": []}
                            st.session_state.active_chat = "Chat 1"
                            st.session_state.chat_counter = 1
                    st.rerun()

        return persona

    def render(self):
        selected_persona = self._handle_sidebar()
        chat_col, info_col = st.columns([7, 3])

        with chat_col:
            st.subheader(f"💬 Active: {st.session_state.active_chat}")
            messages = st.session_state.chat_sessions[st.session_state.active_chat]

            for msg in messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            if user_input := st.chat_input("Type here..."):
                st.session_state.chat_sessions[st.session_state.active_chat].append(
                    {"role": "user", "content": user_input})
                self.db.save_chat_message(st.session_state.active_chat, "user", user_input)

                with st.chat_message("user"):
                    st.markdown(user_input)

                with st.chat_message("assistant"):
                    stream = self.ai.get_response_stream(selected_persona, user_input)
                    response = st.write_stream(stream)

                st.session_state.chat_sessions[st.session_state.active_chat].append(
                    {"role": "assistant", "content": response})
                self.db.save_chat_message(st.session_state.active_chat, "assistant", response)

                st.rerun()

        with info_col:
            st.subheader("System Stats")
            st.info(f"Model: {self.ai.llm.model}")
            st.write(f"Messages in this session: {len(messages)}")
if __name__ == "__main__":
    db = DatabaseHandler()
    engine = AIEngine(model_name="phi3")
    ui = ChatUI(db, engine)
    ui.render()