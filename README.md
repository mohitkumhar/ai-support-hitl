# AI Support Agent Dashboard (HITL)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=flat&logo=mongodb&logoColor=white)](https://www.mongodb.com/)

**Repository:** [http://github.com/mohitkumhar/ai-support-hitl/](http://github.com/mohitkumhar/ai-support-hitl/)

## 📋 Overview

The **AI Support Human-in-the-Loop (HITL) Dashboard** is an intelligent customer support system designed to assist human agents by automating the initial drafting of responses. It leverages **Retrieval-Augmented Generation (RAG)** to ensure responses are grounded in company policy and consistent with past resolved tickets.

The system features a **Streamlit** dashboard where agents can review, edit, rephrase, and approve AI-generated drafts, ensuring high-quality support while reducing response times.

## ✨ Features

-   **🤖 AI Response Drafting**: Automatically generates policy-compliant responses for incoming tickets using OpenAI GPT models.
-   **📚 RAG Context Engine**: Retrieves relevant company policies and similar past tickets (using ChromaDB) to provide context-aware answers.
-   **Human-in-the-Loop Workflow**:
    -   **Pending**: View new tickets waiting for action.
    -   **Drafted**: Review AI-generated drafts with confidence scores.
    -   **Escalated**: Handle complex issues requiring senior attention.
    -   **Completed**: Archive of resolved tickets.
-   **✍️ AI Rephasing Tool**: Allows agents to instantly rewrite responses to be more polite, professional, or empathetic using a temperature slider.
-   **📊 Confidence Scoring**: AI assigns a confidence score to drafts, alerting agents when manual review is critical.
-   **🗄️ Database Integration**: Full persistence using MongoDB for ticket lifecycle management.

## 🛠️ Tech Stack

-   **Frontend**: [Streamlit](https://streamlit.io/)
-   **LLM Orchestration**: [LangChain](https://www.langchain.com/)
-   **LLM Provider**: OpenAI (GPT-4o-mini)
-   **Vector Database**: [ChromaDB](https://www.trychroma.com/)
-   **Database**: [MongoDB](https://www.mongodb.com/)
-   **Language**: Python 3.10+

## 📂 Project Structure

```text
ai-support-hitl/
├── app/
│   ├── main.py                  # Main Streamlit dashboard logic
│   ├── utils.py                 # Utilities for DB, LLM, and Vector Store
│   ├── fetches_from_db.py       # Background service for AI drafting
│   ├── logger.py                # Logging configuration
│   └── response_drafting_utils.py # Pydantic schemas
├── data/
│   └── raw/policy/              # Company policy documents
├── scripts/
│   └── sample_data_generation.py # Script to seed MongoDB with test data
├── .env                         # Environment variables (not committed)
├── streamlit_app.py             # Entry point for the application
└── README.md                    # Project documentation
```

## 🚀 Getting Started

### Prerequisites

-   Python 3.10 or higher
-   MongoDB (Local or Atlas) running on port `27017`
-   OpenAI API Key

### Installation

1.  **Clone the repository**
    ```bash
    git clone http://github.com/mohitkumhar/ai-support-hitl/
    cd ai-support-hitl
    ```

2.  **Create a virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables**
    Create a `.env` file in the root directory:
    ```ini
    OPEN_AI_KEY=sk-your-openai-key-here
    MONGO_URI=mongodb://localhost:27017/
    ```

5.  **Create Logs Directory**
    Ensure a logs directory exists for the application logger.
    ```bash
    mkdir logs
    ```

## 🏃‍♂️ Usage Guide

### 1. Generate Sample Data
Populate your local MongoDB with sample tickets (Pending, Drafted, Solved, Escalated).
```bash
python scripts/sample_data_generation.py
```

### 2. Start the AI Drafting Service
Run the background worker that watches for new pending tickets and drafts responses using the LLM.
```bash
python app/fetches_from_db.py
```
*Keep this terminal open.*

### 3. Launch the Dashboard
Start the Streamlit interface for the support agents.
```bash
streamlit run streamlit_app.py
```

## 🤝 Contributing

Contributions are welcome! Please check the `.github` folder for issue templates and pull request templates.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request
