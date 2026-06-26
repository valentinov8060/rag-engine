# 🤖 RAG Engine

---

## ⚡ Getting Started (Local Development)

1. Prerequisites
   Ensure you have Python 3.12 (Stable LTS) installed on your machine. Avoid experimental versions (e.g., Python 3.14) to prevent compilation issues with scientific binaries like NumPy.

2. Environment Setup
   Clone the repository and navigate into the project directory:

```bash
cd rag-engine
```

Create a virtual environment and activate it:

```bash
# Windows (PowerShell)
python -3.12 -m venv venv
.\venv\Scripts\Activate.ps1

# Windows (Command Prompt)
.\venv\Scripts\activate.bat

# macOS / Linux
python3.12 -m venv venv
source venv/bin/activate
```

3. Install Dependencies
   Install the strictly versioned dependencies inside your active virtual environment:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

4. Configuration (.env)
   Create a .env file in the root directory and add your credentials:

```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
QDRANT_URL=https://xxxxxx.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GROQ_MODEL_NAME=llama-3.1-8b-instant
```

5. Running the Application
   Launch the local Uvicorn development server with live-reload enabled:

```bash
python -m uvicorn app.main:app --reload
```

The terminal will confirm execution with:
INFO: Uvicorn running on http://127.0.0.1:8000

- Open your browser and navigate to http://127.0.0.1:8000/docs to explore the interactive Swagger UI Documentation.

6. Running with Docker
   Build the Docker image locally:

```bash
docker build -t rag-engine .

docker run -d --name rag-engine-container -p 8000:8000 --env-file .env rag-engine:latest
```

---
