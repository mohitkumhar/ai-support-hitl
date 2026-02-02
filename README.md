# 🧠 AI Support HITL

**AI Support HITL** is a **Human-in-the-Loop (HITL)** support assistant built to help support teams draft, refine, review, and escalate support issues using AI—while keeping humans in control.

The app uses **LLMs + Vector DB (RAG)** and provides a **Streamlit UI** for interaction, feedback, and issue raising.

---

## ✨ Key Features

- 🤖 AI-assisted support response drafting
- ✍️ Human-in-the-Loop review and correction
- 📚 Context-aware answers using Vector Database (RAG)
- 🐞 Issue raising option directly from the app
- 📈 Logs & observability support
- 🧪 Testable and modular architecture
- 🐳 Docker & Docker-Compose support

---

## 📂 Project Structure

```

.
├── .github/                    # GitHub workflows and configs
├── Company_Info_VectorDB/      # Vector DB files (company knowledge base)
├── app/                        # Core application logic
├── data/                       # Input/output data
├── logs/                       # Application logs
├── notebooks/                  # Experiments and exploration
├── scripts/                    # Helper scripts
├── tests/                      # Unit & integration tests
├── .dockerignore
├── .flake8
├── .gitignore
├── .pylintrc
├── .python-version
├── Dockerfile
├── docker-compose.yaml
├── promtail-config.yml         # Log shipping configuration
├── requirements.txt
├── pyproject.toml
├── uv.lock
├── streamlit_app.py            # Streamlit entry point
├── application_version.txt
├── LICENSE
└── README.md

````

---

## 🧠 Human-in-the-Loop (HITL) Flow

1. User submits a support query  
2. AI generates a draft response using context from Vector DB  
3. Human reviews, edits, or approves the response  
4. Feedback is logged for improvement  
5. Issues can be raised directly from the UI if needed  

This ensures **accuracy, safety, and quality** in production support workflows.

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/mohitkumhar/ai-support-hitl.git
cd ai-support-hitl
````

---

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

(Optional but recommended: use a virtual environment)

---

### 3️⃣ Environment Variables

Create a `.env` file and add required API keys:

```env
OPEN_AI_KEY=your_api_key
MONGO_URI=your_mongo_uri
```

---

### 4️⃣ Run the Application

```bash
streamlit run streamlit_app.py
```

Open browser at:
📍 `http://localhost:8501`

---

## 🐳 Run with Docker

### Build & Start

```bash
docker compose up --build
```

---

<!--
## 🧪 Run Tests

```bash
pytest
```
---

-->


## 📊 Logging & Observability

* Logs are stored in the `logs/` directory
* `promtail-config.yml` can be used with **Grafana Loki**
* Helps track AI behavior, feedback, and errors

---

## 🔒 License

This project is licensed under the **MIT License**.
See the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Mohit Kumhar**
GitHub: [https://github.com/mohitkumhar](https://github.com/mohitkumhar)  
LinkedIn: [https://linkedin.com/in/mohitkumhar](https://linkedin.com/in/mohitkumhar)  
LeetCode: [https://leetcode.com/mohitkumhar](https://leetcode.com/mohitkumhar)  

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes with clear messages
4. Open a Pull Request

---

## ⭐ If you like this project

Give the repo a ⭐ and feel free to raise issues or suggestions!
