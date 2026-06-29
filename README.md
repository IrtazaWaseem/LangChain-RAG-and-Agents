# 🤖 LangChain, RAG, & Agents Monorepo

Welcome to my AI engineering portfolio repository. This monorepo tracks my progress and projects focused on Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), and complex Agentic routing. 

The goal of this repository is to showcase practical, end-to-end AI applications that interact seamlessly with external environments, including structured relational databases, cloud vector stores, and unstructured document streams.

---

## 📂 Repository Structure

### 1. [Agentic PC Hardware Registry](./AGENTIC-PC-REGISTRY)
A full-stack, AI-powered hardware compatibility engine and tracking dashboard. This module orchestrates different data streams to allow an intelligent agent to make real-time decisions regarding PC builds and game requirements.
* **The Brain:** An integrated LLM Agent that contextualizes user hardware setups to deliver personalized gaming compatibility advice.
* **The Relational Core (Oracle SQL):** Handles the structured data routing and CRUD admin portal.
* **The Telemetry Engine (MongoDB):** Silently logs frame-rate predictions and renders interactive analytics.

### 2. [Smart PDF Chatbot](./SMART-PDF-CHATBOT)
A production-ready Retrieval-Augmented Generation (RAG) pipeline designed to process, chunk, and retrieve insights from user-uploaded PDFs dynamically.
* **Multi-Vector Retrieval:** Utilizes a parent-child chunking strategy (LangChain) backed by **Pinecone** for highly accurate, context-aware retrieval.
* **Stateful Memory:** Implements `RunnableWithMessageHistory` to maintain conversational context across multiple turns without leaking context between sessions.
* **Optimized Cloud Compute:** Dynamically purges orphaned vectors from the Pinecone cloud environment upon session reset to maintain a pristine, zero-bloat database.

### 3. [Omni-Routing Agent](./OMNI-ROUTING-AGENT)
An intelligent routing system designed to classify and direct user queries to specialized sub-agents or specific data pipelines. This project demonstrates foundational agentic decision-making.

### 4. [Simple Chatbot](./SIMPLE-CHATBOT)
A baseline interactive LLM application establishing the core architecture for memory management, prompt engineering, and conversational UI implementation.

---

## 🛠️ Core Tech Stack

* **AI & Orchestration:** Python, LangChain, LLM APIs (Gemini, Groq, Nomic)
* **Databases:** Pinecone (Vector), Oracle SQL (Relational), MongoDB (NoSQL), SQLite (Local Ledgers)
* **Frontend & Visualization:** Streamlit, Plotly, Pandas
* **Architecture:** Monorepo, Multi-Database Routing, Parent-Child RAG chunking

---

## 🚀 Quick Start & Installation

Because this is a monorepo, each project module has its own isolated dependency list. To run a specific module locally:

```bash
# 1. Clone the repository
git clone [https://github.com/IrtazaWaseem/LangChain-RAG-and-Agents.git](https://github.com/IrtazaWaseem/LangChain-RAG-and-Agents.git)
cd LangChain-RAG-and-Agents

# 2. Create and activate a global virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# 3. Navigate to the project you want to run (e.g., the PDF Chatbot)
cd SMART-PDF-CHATBOT

# 4. Install that specific module's dependencies
pip install -r requirements.txt
# 5. run below command to run project
streamlit run app.py
