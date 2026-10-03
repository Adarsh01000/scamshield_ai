# ScamShield AI 🛡️
### AI-Based Multi-Modal Scam Detection & Explainable Risk Assessment
*College Mini Project • 100 Marks Rubric Complete Implementation*

ScamShield AI is an orchestrated multi-agent cybersecurity platform that analyzes SMS, WhatsApp messages, emails, website URLs, and image screenshots to detect fraudulent indicators, calculate an auditable 0–100 risk score, explain why the content is deceptive, and provide actionable remediation advice.

---

## 🚀 Key Features (v1.0)
- **Multi-Modal Ingestion**: Handles SMS/WhatsApp text, URLs, screenshots (PNG/JPG/WEBP), and combined messages.
- **Orchestrator Agent**: Automatically detects modality and coordinates specialized forensic sub-agents.
- **NLP Agent**: Scans for urgency, coercive legal threats, credential requests (OTP/PIN/CVV), fake KYC updates, and lottery/task scams.
- **URL ML Classifier Agent**: Extracts 16 lexical, structural, and Shannon entropy features; powered by a trained **Random Forest Classifier**.
- **OCR & Vision Agents**: Extracts embedded text and hyperlinks from screenshots; analyzes visual urgency banners.
- **Evidence Agent**: Compiles forensic findings into a standardized, auditable schema with confidence levels.
- **Risk Fusion Agent**: Calibrated 0–100 risk score calculation with transparent weights and multi-modal correlation boost.
- **Explanation Agent**: Grounded explanation strictly tied to verified evidence, with optional Google Gemini GenAI integration.
- **Evaluation Agent**: Automated benchmark suite reporting precision, recall, F1, confusion matrices, and multi-modal ablation comparisons.
- **Dual Interfaces**: Sleek **Streamlit Web Dashboard** and high-throughput **FastAPI REST API**.

---

## 🏗️ Architecture & Agent Pipeline

```
[ User Input: SMS / Email / URL / Screenshot ]
                      │
                      ▼
          [ Orchestrator Agent ]
       ┌──────────────┼──────────────┬──────────────┐
       ▼              ▼              ▼              ▼
 [ NLP Agent ]   [ URL Agent ]  [ OCR Agent ]  [ Vision Agent ]
       │              │              │              │
       └──────────────┼──────────────┴──────────────┘
                      ▼
             [ Evidence Agent ]
                      │
                      ▼
           [ Risk Fusion Agent ]  (Normalized 0–100 Score)
                      │
                      ▼
          [ Explanation Agent ]  (Grounded strictly in Evidence)
                      │
                      ▼
    [ Streamlit & FastAPI Dashboards ]
```

---

## 📦 Setup & Installation

### 1. Activate Environment
On Windows PowerShell:
```powershell
.\venv\Scripts\activate
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Environment Configuration
Inspect or edit `.env`:
```env
APP_NAME="ScamShield AI"
VERSION="1.0"
ENVIRONMENT="development"
# Optional: Provide Google Gemini API Key for enhanced LLM explanations
GEMINI_API_KEY=""
GEMINI_MODEL="gemini-2.5-flash"
# Optional: Path to Tesseract OCR executable if installed
TESSERACT_CMD="C:\Program Files\Tesseract-OCR\tesseract.exe"
```

---

## ⚡ Execution Commands & 1-Click Launchers

### 🖱️ Option A: 1-Click Desktop Shortcut (Easiest)
- Double-click the **`ScamShield AI`** shortcut directly on your **Windows Desktop**.
- It starts the server and immediately opens `http://localhost:8501` in your browser.
*(To re-generate the shortcut anytime, run `.\venv\Scripts\python scripts/create_desktop_shortcut.py`)*

### 🚀 Option B: 1-Click Batch Launchers
- **Streamlit Web Application**: Double-click [`Launch_ScamShield_AI.bat`](file:///c:/Users/DELL/OneDrive/Desktop/scam%20shield%20ai%20mini%20project/Launch_ScamShield_AI.bat)
- **FastAPI REST Backend**: Double-click [`Launch_FastAPI_Backend.bat`](file:///c:/Users/DELL/OneDrive/Desktop/scam%20shield%20ai%20mini%20project/Launch_FastAPI_Backend.bat)

### 💻 Option C: Terminal Execution
```powershell
# Launch Streamlit Web UI
.\venv\Scripts\python -m streamlit run src/main.py

# Launch FastAPI REST Server
.\venv\Scripts\python -m uvicorn src.api:app --reload --port 8000

# Run Automated Unit Tests (18 passing tests)
.\venv\Scripts\pytest

# Run Evaluation Benchmark & Ablation Study
.\venv\Scripts\python -m src.agents.evaluation
```


## 📊 Experimental Evaluation Results

| Modality Configuration | Accuracy | Precision | Recall | F1-Score | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Text-Only** | 50.0% | 1.000 | 0.250 | 0.400 | Baseline |
| **URL-Only** | 83.3% | 0.800 | 1.000 | 0.889 | High URL recall |
| **Screenshot/OCR-Only** | 66.7% | 0.750 | 0.750 | 0.750 | Parses captures |
| **Text + URL** | 100.0% | 1.000 | 1.000 | 1.000 | Dual channel |
| **Full Multi-Modal Fusion** | **100.0%** | **1.000** | **1.000** | **1.000** | **State of the Art** |

---

## 📑 Project Report & Viva Deliverables
Complete documentation aligned with the **100-mark college assessment** is available in:
👉 [`PROJECT_REPORT_AND_VIVA.md`](file:///c:/Users/DELL/OneDrive/Desktop/scam%20shield%20ai%20mini%20project/PROJECT_REPORT_AND_VIVA.md)

Contains:
1. Problem Statement & Motivation (5 Marks)
2. Literature Survey & Existing System Comparison (5 Marks)
3. Scope, Objectives & Proposed System (20 Marks)
4. System Design & 6 UML Diagrams (Use Case, Activity, Sequence, Component, Class, Deployment) (15 Marks)
5. Requirements Specification & Test Cases Matrix (10 Marks)
6. Methodology, URL Random Forest & Risk Fusion Formulation (15 Marks)
7. Evaluation Benchmarks & Ablation Studies (10 Marks)
8. College Viva Voce Comprehensive Q&A Guide (10 Marks)
