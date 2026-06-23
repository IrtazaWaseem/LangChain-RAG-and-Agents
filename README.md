# 🤖 LangChain, RAG, & Agents Monorepo

Welcome to my AI engineering portfolio repository. This monorepo tracks my progress and projects focused on Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), and complex Agentic routing. 

The goal of this repository is to showcase practical, end-to-end AI applications that interact seamlessly with external environments, including structured relational databases and unstructured NoSQL telemetry streams.

---

## 📂 Repository Structure

### 1. [Agentic PC Hardware Registry](./AGENTIC-PC-REGISTRY)
A full-stack, AI-powered hardware compatibility engine and tracking dashboard. This module orchestrates different data streams to allow an intelligent agent to make real-time decisions regarding PC builds and game requirements.

**Key Features:**
* **The Brain:** An integrated LLM Agent that contextualizes user hardware setups and queries system specs to deliver personalized gaming compatibility and upgrade advice.
* **The Relational Core (Oracle SQL):** Handles the structured data routing, including custom PC builds, game requirements, hardware tiers, and a fully functional CRUD admin portal.
* **The Telemetry Engine (MongoDB):** Silently logs frame-rate predictions in the background and renders interactive frame-time analytics.
* **The Frontend (Streamlit):** Optimized for real-time state management and interactive WebGL/Plotly visualizations.

### 2. [Omni-Routing Agent](./OMNI-ROUTING-AGENT)
An intelligent routing system designed to classify and direct user queries to specialized sub-agents or specific data pipelines. This project demonstrates foundational agentic decision-making and context preservation across multiple turns.

### 3. [Simple Chatbot](./SIMPLE-CHATBOT)
A baseline interactive LLM application establishing the core architecture for memory management, prompt engineering, and basic conversational UI implementation.

---

## 🛠️ Core Tech Stack

* **AI & Orchestration:** Python, LangChain, LLM APIs
* **Databases:** Oracle SQL (Relational), MongoDB (NoSQL)
* **Frontend & Visualization:** Streamlit, Plotly, Pandas
* **Architecture:** Monorepo, Environment Variable Security, Multi-Database Routing

---

## 🚀 Quick Start & Installation

To run any of these modules locally, clone the repository and set up your virtual environment:

```bash
# Clone the repository
git clone [https://github.com/IrtazaWaseem/LangChain-RAG-and-Agents.git](https://github.com/IrtazaWaseem/LangChain-RAG-and-Agents.git)
cd LangChain-RAG-and-Agents

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install dependencies
pip install -r AGENTIC-PC-REGISTRY/requirements.txt
