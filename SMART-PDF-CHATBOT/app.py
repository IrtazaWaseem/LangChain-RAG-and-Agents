import streamlit as st
import os
import tempfile
import uuid
import logging
from langchain_classic.storage._lc_store import create_kv_docstore

from core.ingestion import PDFParser
from core.splitting import DocumentSplitter
from core.embeddings import EmbeddingsProvider
from core.vectorstore import VectorStoreManager
from core.retrieval import AdvancedRetriever
from core.generation import RAGPipeline
from core.memory import MemoryManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

st.set_page_config(page_title="PDF Chatbot", page_icon="📄", layout="wide")
st.markdown("""<style>
    /* Main App Background and Base Font */
    .stApp {
        background-color: Black;
        color: White;
        font-family: sans-serif;
    }

    /* Document Width Setup */
    .block-container {
        max-width: 900px !important;
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
    }

    /* Sidebar Layout Setup */
    [data-testid="stSidebar"] {
        background-color: White !important;
        border-right: 1px solid LightGray;
    }
    [data-testid="stSidebar"] * {
        color: Black !important;
    }

    /* Chat Input Styling */
    [data-testid="stChatInput"] {
        background-color: Black !important;
        border: none !important;
    }
    .stChatInputContainer {
        background-color: DarkSlateGray !important;
        border-radius: 14px !important;
        border: 1px solid Gray !important;
    }

    /* Chat Message Container & HIGH-CONTRAST Typography */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        gap: 0.5rem !important;
    }

    /* User Message Bubble */
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: DarkSlateGray !important;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid DimGray;
    }

    /* Assistant Message Bubble */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #111111 !important;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid DimGray;
    }

    /* FORCE Crisp White Text & Clean Visibility inside Chat Bubbles */
    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] li, 
    [data-testid="stChatMessage"] span,
    [data-testid="stChatMessage"] div {
        color: White !important;
        font-size: 1.05rem !important;
        line-height: 1.6 !important;
    }

    /* Bold Elements Highlighting */
    [data-testid="stChatMessage"] strong {
        color: Gold !important;
        font-weight: bold !important;
    }

    /* Hide Avatars & Streamlit Boilerplate */
    [data-testid="stChatMessageAvatar"] { display: none !important; }
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Buttons */
    .stButton>button {
        border-radius: 10px !important;
        border: 1px solid Gray !important;
        background-color: DimGray !important;
    }
    .stButton>button * {
        color: White !important;
        font-weight: bold !important;
    }
    .stButton>button:hover {
        background-color: Gray !important;
    }
    </style>""", unsafe_allow_html=True)


@st.cache_resource
def initialize_infrastructure():
    """Initializes global backend connections exactly once."""
    provider = EmbeddingsProvider(model_name="nomic-embed-text")
    embed_model = provider.get_embeddings()
    db_manager = VectorStoreManager(embedding_model=embed_model, index_name="new-database")
    memory_manager = MemoryManager()
    return db_manager, memory_manager


app_db, app_memory = initialize_infrastructure()

# --- STATE INITIALIZATION ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.is_processed = False
    st.session_state.messages = []

# --- PIPELINE OPTIMIZATION FIX ---
# We store the chain in session_state so it doesn't rebuild on every keystroke,
# but we tie it to the current session_id so it resets properly on "New Session".
if "user_chain" not in st.session_state or st.session_state.get("chain_session_id") != st.session_state.session_id:
    retriever_engine = AdvancedRetriever(
        vectorstore=app_db.vector_store,
        docstore=app_db.store
    ).get_retriever(namespace=st.session_state.session_id, k=30)

    rag_engine = RAGPipeline(retriever=retriever_engine)
    st.session_state.user_chain = app_memory.get_stateful_chain(rag_engine.get_chain())
    st.session_state.chain_session_id = st.session_state.session_id

with st.sidebar:
    st.markdown("### Controls")
    uploaded_files = st.file_uploader("Upload Docs", type=["pdf"], accept_multiple_files=True)

    if st.button("Process", type="primary") and uploaded_files:
        with st.spinner("Indexing..."):
            for actual_file in uploaded_files:

                tmp_path = None

                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:

                        # FIXED: # type: ignore tells the IDE to stop guessing Streamlit's return types
                        tmp_file.write(actual_file.getvalue())  # type: ignore
                        tmp_path = tmp_file.name

                    parser = PDFParser(mode="fast")
                    raw_docs = list(parser.load_file(tmp_path))

                    splitter = DocumentSplitter()
                    parents, children = splitter.split_documents(raw_docs)
                    kv_store = create_kv_docstore(app_db.store)
                    parent_pairs = [(p.metadata["doc_id"], p) for p in parents]
                    kv_store.mset(parent_pairs)

                    for child in children:
                        child.metadata = app_db.sanitize_metadata(child.metadata)
                        child.metadata["namespace"] = st.session_state.session_id

                    app_db.vector_store.add_documents(children, namespace=st.session_state.session_id)
                finally:
                    if tmp_path and os.path.exists(tmp_path):
                        os.remove(tmp_path)

            st.session_state.is_processed = True
            st.toast("Ready!", icon="✅")

    if st.button("New Session"):
        # FIXED: Directly invoke Pinecone SDK to wipe the cloud namespace
        try:
            index = app_db.pc.Index(app_db.index_name)
            index.delete(delete_all=True, namespace=st.session_state.session_id)
        except Exception as e:
            logging.error("Failed to clear Pinecone namespace: %s", e)

        app_memory.clear_session(st.session_state.session_id)
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.is_processed = False
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        config = {"configurable": {"session_id": st.session_state.session_id}}

        try:
            for chunk in st.session_state.user_chain.stream({"question": user_input}, config=config):
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        except Exception:
            logging.exception("Chain failed during streaming.")
            message_placeholder.markdown("Something went wrong. Please try again.")