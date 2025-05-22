# ATS


📄 README.txt — Run AI Resume Chat App Locally

✅ Requirements

1. Python 3.10+ installed
2. VS Code
3. Ollama installed locally: https://ollama.com/download
4. Models:
   - llama2
   - nomic-embed-text

Install these models via terminal:
    ollama run llama2
    ollama pull nomic-embed-text

📁 Folder Structure

ai_resume_chat_pro/
│
├── app.py                   # Streamlit main app
├── rag_pipeline.py          # RAG logic (vector store + chatbot)
├── ranker.py                # Candidate scoring
├── resume_parser.py         # Resume text extraction
├── summarizer.py            # AI-generated summaries
├── requirements.txt         # Dependencies
└── README.txt               # This file

⚙️ Setup Instructions

1. Clone/Unzip Project

If you downloaded a ZIP file, extract it in a folder:
    cd ai_resume_chat_pro

2. Create Virtual Environment
    python -m venv myenv
    source myenv/bin/activate     # On Windows: myenv\Scripts\activate

3. Install Dependencies
    pip install -r requirements.txt

4. Start Ollama Server
    ollama serve

Then load the required model:
    ollama run llama2

(Keep this terminal open)

5. Run the Streamlit App
    streamlit run app.py

Your browser should open at:
    http://localhost:8501

💡 Features

- Upload multiple resumes (PDF/DOCX)
- Analyze and rank candidates based on job description
- View candidate insights and scores
- Chat with an AI to explore resume details

❗ Troubleshooting

- Embedding Error?
    Ensure nomic-embed-text is pulled:
        ollama pull nomic-embed-text

- Connection refused?
    Make sure you ran:
        ollama serve
