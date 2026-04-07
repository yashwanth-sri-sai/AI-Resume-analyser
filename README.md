# 🚀 AI Resume Analyzer

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google_Gemini-AI-4285F4?style=for-the-badge&logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**An advanced, production-grade AI Resume Analyzer with ATS scoring, job matching, and AI-powered coaching.**

[Live Demo](#) · [Report Bug](#) · [Request Feature](#)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 **ATS Resume Scoring** | 8-category ATS compliance check with scores 0-100 |
| 🤖 **AI Analysis** | Google Gemini-powered deep resume analysis |
| 💼 **Job Matching** | TF-IDF cosine similarity with job descriptions |
| 🔑 **Keyword Gap Analysis** | Identify missing keywords from job listings |
| 🛠️ **Skill Gap Analysis** | Compare your skills vs job requirements |
| 📊 **Analytics Dashboard** | Plotly charts — radar, bar, gauges, trends |
| 💬 **AI Chat Coach** | Interactive career coaching chatbot |
| 🔐 **User Authentication** | Secure accounts with bcrypt password hashing |
| 📁 **Analysis History** | Save, track, and download past analyses |
| 📥 **PDF Reports** | Downloadable professional PDF reports |

---

## 🏗️ Architecture

```
ai-resume-analyzer/
├── app.py                     # 🏠 Landing page
├── pages/
│   ├── 1_📄_Resume_Analysis.py  # Core analysis page
│   ├── 2_💼_Job_Matching.py     # JD matching
│   ├── 3_📊_Analytics.py        # Visual analytics
│   ├── 4_💬_AI_Chat.py          # AI coaching chat
│   ├── 5_🔐_Authentication.py   # Login/register
│   └── 6_📁_History.py          # Past analyses
├── utils/
│   ├── file_parser.py           # PDF/DOCX extraction
│   ├── text_processor.py        # NLP processing
│   ├── ats_scorer.py            # ATS scoring
│   ├── keyword_extractor.py     # TF-IDF keywords
│   ├── skill_analyzer.py        # Skill gap analysis
│   ├── db_manager.py            # SQLite database
│   ├── auth.py                  # Authentication
│   ├── report_generator.py      # PDF reports
│   └── llm_client.py            # Gemini AI client
├── models/
│   ├── ml_scorer.py             # ML scoring
│   └── similarity.py            # Cosine similarity
├── data/
│   ├── skills_db.json           # 200+ skills taxonomy
│   └── job_roles.json           # 15 job role templates
└── assets/
    └── style.css                # Custom dark theme CSS
```

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/yourusername/ai-resume-analyzer.git
cd ai-resume-analyzer
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

Get your free Gemini API key at: https://aistudio.google.com/

### 3. Run the App

```bash
streamlit run app.py
```

The app opens at **http://localhost:8501** 🎉

---

## 🔧 ATS Scoring Algorithm

The ATS score is calculated across **8 weighted categories**:

| Category | Weight | What it checks |
|----------|--------|----------------|
| Contact Information | 10% | Email, phone, LinkedIn, GitHub |
| Section Structure | 15% | Presence of all key sections |
| Content Length | 10% | Optimal word count (300-800 words) |
| Action Verbs | 10% | Strong verbs like "led, built, achieved" |
| Quantified Achievements | 15% | Numbers, percentages, dollar amounts |
| Skills Section | 15% | Dedicated skills with relevant tech |
| Education | 10% | Education section present |
| Work Experience | 15% | Experience section with details |

---

## 🤖 AI Features

Powered by **Google Gemini 1.5 Flash**:
- **Resume Analysis**: Strengths, improvements, career level assessment
- **Job Matching**: Fit assessment, critical gaps, interview prep topics
- **Chat Coach**: Context-aware career coaching on any resume question

> **Note**: The app works in Demo Mode without an API key (mock AI responses). Add your Gemini API key for real AI analysis.

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit + Custom CSS (dark theme)
- **AI**: Google Gemini 1.5 Flash
- **NLP**: TF-IDF Vectorization, cosine similarity
- **Database**: SQLite + SQLAlchemy ORM
- **Auth**: bcrypt password hashing
- **Charts**: Plotly
- **File Parsing**: pdfplumber, python-docx
- **Reports**: reportlab PDF generation

---

## 📦 Deployment

### Streamlit Cloud (Free)
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo and add `GEMINI_API_KEY` as a secret

### Render.com
```bash
# The Procfile is already configured
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

---

## 📜 License

MIT License — free to use for personal and commercial projects.

---

## 🙏 Built With

- [Streamlit](https://streamlit.io) — Web app framework
- [Google Gemini AI](https://aistudio.google.com) — AI analysis
- [scikit-learn](https://scikit-learn.org) — TF-IDF similarity
- [pdfplumber](https://github.com/jsvine/pdfplumber) — PDF extraction
- [reportlab](https://reportlab.com) — PDF generation
- [Plotly](https://plotly.com) — Interactive charts
