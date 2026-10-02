# 🧠 CATALYST: Context Aware Teaching & Learning System

<p align="center">
  <img src="https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js" alt="Next.js">
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=for-the-badge&logo=typescript" alt="TypeScript">
  <img src="https://img.shields.io/badge/FAISS-Vector_Search-blue?style=for-the-badge" alt="FAISS">
  <img src="https://img.shields.io/badge/Groq_API-Cloud_LLM-orange?style=for-the-badge" alt="Groq">
  <img src="https://img.shields.io/badge/Ollama-Local_Failover-white?style=for-the-badge" alt="Ollama">
</p>

**CATALYST** is an enterprise-grade, highly resilient Retrieval-Augmented Generation (RAG) platform designed for precision document analysis, strict context isolation, and high-confidence questioning. Engineered with an industrial minimalist aesthetic, CATALYST seamlessly ingests multi-format documents, processes them through a hybrid dense-sparse retrieval pipeline with cross-encoder re-ranking, and leverages a multi-tier LLM architecture featuring automatic cloud-to-local failover.

---

## 🎯 Problem Statement & Pain Points

Modern organizations deal with vast repositories of unstructured documents (PDFs, DOCX files, reports). Traditional document analysis and standard naive RAG pipelines suffer from critical flaws:

1. **Hallucinations & Retrieval Failure**: Naive vector search often fails to capture precise keywords, domain jargon, or exact match queries (e.g., product IDs, invoice numbers), leading to irrelevant context and AI hallucinations.
2. **Cloud API Dependency & Downtime**: Relying solely on cloud-hosted LLMs introduces single points of failure. Rate limits, network hiccups, or cloud provider outages disrupt critical operational workflows.
3. **Black-Box Responses & Lack of Trust**: Users cannot verify the validity of AI-generated answers without direct, transparent source citations back to exact document chunks.
4. **Data Contamination across Projects**: Mixing multi-tenant or multi-project documents without strict workspace boundaries risks context leakage and privacy breaches.

---

## 💡 Core Ideation & Solution Architecture

CATALYST was built to overcome these challenges by combining state-of-the-art information retrieval techniques with bulletproof system reliability:

* **Hybrid Retrieval (FAISS + BM25)**: Blends dense semantic vector search (FAISS) with sparse lexical keyword matching (BM25Okapi) using Reciprocal Rank Fusion (RRF) to maximize both semantic understanding and keyword accuracy.
* **Cross-Encoder Re-Ranking**: Filters retrieved candidate chunks through a cross-encoder model to re-score relevance, keeping only high-confidence contexts before injecting into the prompt.
* **Zero-Downtime LLM Failover**: Automatically routes requests to high-speed cloud inference (Groq API), and gracefully falls back to local offline models (Ollama - Qwen) if cloud rate limits or connectivity issues occur.
* **Strict Workspace Isolation**: Encapsulates documents, embeddings, conversation history, and search indices into isolated project workspaces.
* **Auditable Source Attribution**: Every response provides interactive citations pointing to the exact source document, page, and chunk score.

---

## 🏗️ Architecture & System Design

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                                 FRONTEND (Next.js)                               │
│      Bento Dashboard  │  Workspace Isolation  │  Chat UI  │  Analytics           │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │ REST APIs (HTTP / JSON)
┌────────────────────────────────────────▼─────────────────────────────────────────┐
│                                 BACKEND (FastAPI)                                │
│   ┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐ │
│   │   Ingestion Service   │  │  Hybrid RAG Pipeline  │  │  Failover LLM Router  │ │
│   └───────────┬───────────┘  └───────────┬───────────┘  └───────────┬───────────┘ │
└───────────────┼──────────────────────────┼──────────────────────────┼────────────┘
                │ Async Ingestion          │ Hybrid Search            │ Inference
┌───────────────▼───────────┐  ┌───────────▼───────────┐  ┌───────────▼────────────┐
│   DOCUMENT PROCESSING     │  │   RETRIEVAL ENGINES   │  │     LLM PROVIDERS      │
│   • PyMuPDF / docx        │  │   • FAISS (Dense)     │  │   • Groq API (Cloud)   │
│   • Semantic Chunking     │  │   • BM25 (Sparse)     │  │   • Ollama/Qwen (Local)│
│   • Sentence Transformers │  │   • Cross-Encoder     │  │                        │
└───────────────┬───────────┘  └───────────┬───────────┘  └────────────────────────┘
                │                          │
┌───────────────▼──────────────────────────▼───────────────────────────────────────┐
│                                 STORAGE LAYER                                    │
│       SQLite3 (Metadata, Chats)  │  FAISS Indices  │  BM25 Cache  │  FS Storage   │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Technical Deep Dive & Workflows

### 1. Document Ingestion Pipeline
1. **Parsing & Extraction**: Text is extracted from `PDF` (via PyMuPDF) or `DOCX` files, preserving structural hierarchies and metadata.
2. **Sanitization**: Normalizes whitespace, strips non-printable characters, and standardizes unicode encoding.
3. **Semantic Chunking**: Splits text into sliding window chunks (e.g., 512 tokens with 50-token overlap) to maintain boundary context.
4. **Vector & Lexical Indexing**:
   - Embeddings generated via `sentence-transformers` and stored in a workspace-isolated **FAISS** index.
   - Lexical terms parsed into a workspace-isolated **BM25** index.
   - Document & chunk metadata committed to **SQLite3**.

### 2. Hybrid Retrieval & Generation Pipeline
1. **Dual Query Execution**: Concurrently executes dense vector retrieval on FAISS and sparse keyword retrieval on BM25.
2. **Reciprocal Rank Fusion (RRF)**: Merges and deduplicates candidate chunks from both retrieval methods.
3. **Cross-Encoder Re-Ranking**: Evaluates query-chunk pairs using a Cross-Encoder model, filtering out any chunk falling below a configurable confidence threshold.
4. **Context-Aware Prompt Generation**: Constructs a tightly structured prompt containing exact retrieved context chunks and conversation history.
5. **Multi-Tier Inference & Failover**:
   - **Primary**: Dispatches request to the ultra-fast Groq API.
   - **Failover**: On API error/rate-limit, automatically catches the exception and routes the identical context to a local Ollama instance (Qwen).

---

## ✨ Key Features

* 🏢 **Workspace Management**: Complete multi-project isolation for documents, vector indices, and chat histories.
* 📄 **Multi-Format Processing**: Asynchronous drag-and-drop ingestion for PDF and DOCX files with live status polling.
* 🔍 **Hybrid RAG Engine**: Combines FAISS + BM25 + Cross-Encoder Re-ranking for maximum precision.
* 🤖 **Zero-Downtime Failover**: Seamless automatic transition between Groq API and local Ollama inference.
* 📊 **Telemetry & Analytics**: Recharts-powered dashboard for query volume, storage usage, and system health status.
* 🛡️ **Industrial UI Aesthetics**: Custom token-based design system in Next.js 14 without bloated external UI libraries.

---

## 🛠️ Tech Stack

| Domain | Technologies |
| :--- | :--- |
| **Frontend** | Next.js 14 (App Router), React 18, TypeScript, Zustand, Tailwind CSS, Framer Motion, Recharts |
| **Backend** | Python 3.10+, FastAPI, Uvicorn, Asyncio, Pydantic |
| **RAG & AI** | FAISS, rank_bm25, Sentence-Transformers, Cross-Encoders, PyMuPDF, python-docx |
| **LLMs & Inference** | Groq API (Primary Cloud), Ollama / Qwen (Local Failover) |
| **Storage** | SQLite3, FAISS Index Files, Local File System Storage |

---

## 🚀 Quick Start Guide

### Prerequisites
* **Node.js**: v18.17 or higher
* **Python**: v3.10 or higher
* **Ollama**: Installed and running locally (optional for local failover, e.g. `ollama run qwen:0.5b`)
* **Groq API Key**: (Optional, for cloud LLM inference)

### Easy Launcher (Windows `.bat` Scripts)
The repository includes automated batch scripts in the root directory:
* **`start.bat`**: Launches both the FastAPI backend (Port 8000) and Next.js frontend (Port 3000).
* **`stop.bat`**: Safely finds and terminates any active processes on ports 8000 & 3000.
* **`build.bat`**: Builds the production frontend bundle.
* **`test.bat`**: Runs backend unit tests (`pytest`) and frontend linters.

```cmd
:: To start the application:
start.bat

:: To stop the application:
stop.bat
```

---

### Manual Setup & Installation

#### 1. Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables (.env in root)
echo GROQ_API_KEY=your_groq_api_key_here > .env

# Run FastAPI backend server
python -m uvicorn backend.main:app --reload --port 8000
```
*API docs available at: `http://localhost:8000/docs`*

#### 2. Frontend Setup
```bash
cd frontend

# Install Node dependencies
npm install

# Configure environment variables (.env.local in frontend/)
echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local

# Run Next.js development server
npm run dev
```
*Application available at: `http://localhost:3000`*

---

## 🚀 Cloud Deployment Guide (Zero-Cost Production Setup)

CATALYST is engineered to deploy seamlessly under free-tier cloud architectures:

### 1. Backend Deployment on [Render.com](https://render.com)
Deploy as a Python Web Service using either Docker or native Python runtime:

#### Option A: Infrastructure-as-Code (Blueprint)
1. Push your repository to GitHub.
2. In Render Dashboard, click **New > Blueprint** and select your repository (`render.yaml` will be auto-detected).
3. Provide your environment variables (`GROQ_API_KEY`, `ALLOWED_ORIGINS`).

#### Option B: Manual Web Service
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt && python scripts/download_models.py`
- **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**:
  | Variable | Value | Description |
  | :--- | :--- | :--- |
  | `ENVIRONMENT` | `production` | Enables structured JSON logging & disables debug chatter |
  | `ALLOWED_ORIGINS` | `https://<your-vercel-app>.vercel.app` | Comma-separated CORS origins |
  | `GROQ_API_KEY` | `gsk_...` | Free Groq API key for cloud LLM inference |
  | `MODELS_CACHE_PATH` | `storage/models` | Pre-downloaded model cache |
  | `OFFLINE_MODE` | `true` | Prevents runtime HuggingFace probing |

---

### 2. Frontend Deployment on [Vercel](https://vercel.com)
Deploy the Next.js frontend with zero configuration:
1. In Vercel Dashboard, click **Add New > Project** and import your GitHub repository.
2. In the project setup screen, configure:
   - **Root Directory**: `frontend`
   - **Framework Preset**: `Next.js`
3. Add Environment Variables:
   | Variable | Value | Description |
   | :--- | :--- | :--- |
   | `NEXT_PUBLIC_API_URL` | `https://<your-render-app>.onrender.com` | Live backend Render API URL |
4. Click **Deploy**. Vercel will compile and host the web application on an edge CDN.


## 📂 Project Structure

```text
Implementation_2/
├── backend/                  # FastAPI Application
│   ├── api/                  # API Routers (Workspace, Document, Chat, System, Analytics)
│   ├── core/                 # Exception handlers, Lifespan hooks, Configurations
│   ├── models/               # Pydantic Schemas & Domain Models
│   ├── repositories/         # Database, FAISS, & BM25 Data Access Layers
│   ├── services/             # Business Logic (Ingestion, Hybrid Search, Failover Router)
│   └── main.py               # Application Entrypoint
├── frontend/                 # Next.js 14 Application
│   ├── src/
│   │   ├── app/              # App Router Pages & Layouts
│   │   ├── components/       # Component Architecture (Chat, Workspace, Analytics)
│   │   ├── hooks/            # Custom React Hooks
│   │   ├── services/         # Typed API Fetch Wrappers
│   │   ├── store/            # Zustand State Stores
│   │   └── styles/           # CSS Tokens & Global Styles
│   └── package.json
├── docs/                     # Architecture Plans & System Diagrams
├── start.bat                 # Windows Start Script
├── stop.bat                  # Windows Force-Stop Script (Port 8000 & 3000)
├── build.bat                 # Windows Build Script
├── test.bat                  # Windows Test Script
├── requirements.txt          # Backend Dependencies
└── .gitignore                # Production Git Ignore Configuration
```

---

## 🛡️ License

Distributed under the MIT License. See `LICENSE` for more information.
