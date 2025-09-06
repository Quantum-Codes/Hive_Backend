# 🐝 Hive Backend

A Reddit-like backend with intelligent content verification powered by web scraping and a Gemini-based RAG pipeline.

## 📖 Project Description

Hive provides a FastAPI backend for social media posts with intelligent content verification. Features include:

- **Post Management**: Create, read, update, and delete posts with likes/dislikes
- **User Authentication**: Google OAuth integration via Supabase Auth
- **File Storage**: Image and media upload to Supabase Storage 
- **Content Verification**: Automated fact-checking using:
  - Web scraping for context gathering
  - Google Gemini AI for content analysis
  - ChromaDB vector database for document retrieval
  - RAG (Retrieval-Augmented Generation) pipeline for verification
- **Real-time Processing**: Synchronous verification pipeline during post creation

## 📂 Folder Structure

```
Hive_Backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routers/
│   │       ├── posts.py           # posts CRUD, reactions, listing
│   │       ├── storage.py         # uploads to Supabase Storage
│   │       └── auth.py            # Supabase OAuth, JWT auth helpers
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # settings (Supabase, Gemini, Chroma, etc.)
│   │   └── supabase.py            # Supabase client factory
│   ├── models/
│   │   ├── __init__.py
│   │   ├── rag.py                 # RagRequest/Response enums
│   │   ├── post.py                # User, Post, Comment, ShowPost, tokens
│   │   └── scraper.py             # ScraperResult
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── scrapers/
│   │   │   └── scraper_agent/web_scraper.py
│   │   ├── search_agent/
│   │   │   └── search_agent.py
│   │   └── rag_agent/
│   │       └── rag_agent.py       # Gemini + Chroma pipeline
│   └── services/
│       ├── __init__.py
│       └── verification_service.py # verification orchestration
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   └── test_supabase_client.py
├── pyproject.toml | poetry.lock | requirements.txt
├── setup_env.py | env.example | README.md
└── .chroma/                        # ChromaDB vector database storage
```

## ⚙️ Setup & Installation

### Prerequisites

-   Python 3.13+
-   Supabase project (URL + anon + service role keys)
-   Google Gemini API key for content verification

### Environment Setup

1. Create and activate a virtual environment

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

    Or with Poetry:

    ```bash
    pip install poetry
    poetry install
    poetry run uvicorn app.main:app --reload
    ```

2. Environment variables

    ```bash
    python setup_env.py
    # or
    cp env.example .env
    ```

## ▶️ Running the Server

```bash
uvicorn app.main:app --reload
```

Server: `http://localhost:8000`

### API Docs

-   Swagger UI: `http://localhost:8000/docs`
-   ReDoc: `http://localhost:8000/redoc`

### Health

-   GET `/` → welcome
-   GET `/health` → service health
-   GET `/config/test` → config probe

## 🔐 Authentication (Supabase OAuth)

-   GET `/user/login` → Redirect to Google OAuth
-   GET `/user/users/me` → Get current user (requires `Authorization: Bearer <jwt>`)
-   GET `/user/logout` → Sign out

Use the Supabase session JWT as the Bearer token for authenticated routes.

## 🗃️ Storage

-   POST `/storage/upload/profile-pic` → upload profile picture, updates `users.profile_pic_url`

## 📝 Posts API

Prefix: `/post`

-   POST `/` → create post (body: `Post`), runs verification synchronously
-   GET `/` → list all posts
-   GET `/users/{uid}/posts` → list posts by user
-   GET `/{pid}` → get one post
-   PUT `/{pid}` → update post (owner only)
-   DELETE `/{pid}` → delete post (owner only)
-   POST `/{pid}/like` → increment likes
-   POST `/{pid}/dislike` → increment dislikes
-   POST `/{pid}/verify` → manually trigger verification for a specific post

## 🧠 Verification Pipeline

Content verification is performed synchronously when posts are created using a sophisticated RAG pipeline:

### Architecture
-   **Search Agent**: Finds relevant sources using Google Custom Search
-   **Web Scraper**: Extracts content from discovered sources  
-   **RAG Pipeline**: Uses Google Gemini + ChromaDB for verification
    -   Vectorizes scraped content in ChromaDB
    -   Performs similarity search for relevant context
    -   Analyzes content using Gemini AI
    -   Returns verification status with confidence scores

### Verification Response
`VerificationRAGPipeline.verify(RagRequest)` returns:

```json
{
    "status": "verified | unverified | personal_opinion | misinformation | factual_error | other",
    "confidence": 0.85,
    "answer": "Content analysis summary...",
    "supporting_context": ["Source 1 context...", "Source 2 context..."],
    "rationale": "Explanation of verification decision...",
    "metadata": { "post_id": "..." }
}
```

### Verification Statuses
- **verified**: Content is factually accurate
- **unverified**: Cannot determine accuracy  
- **personal_opinion**: Subjective content
- **misinformation**: Deliberately false information
- **factual_error**: Unintentionally incorrect information
- **other**: Content doesn't fit other categories

## 🧱 Models (Pydantic)

-   `app/models/post.py`
    -   `User`, `Post`, `Comment`, `ShowPost`, `Token`, `TokenData`
    -   `PostContentRequest`, `PostVerificationRequest`
-   `app/models/rag.py`
    -   `RagRequest`, `RagResponse` with verification status enums
-   `app/models/scraper.py`
    -   `ScraperResult` for web scraping results

## 🛠️ Configuration

`app/core/config.py` provides centralized configuration with nested sections:

-   **Supabase**: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
-   **Gemini AI**: `GEMINI_API_KEY`, `GEMINI_MODEL`, `GEMINI_EMBED_MODEL`, `GEMINI_MAX_TOKENS`, `GEMINI_TEMPERATURE`
-   **Search**: `GOOGLE_CUSTOM_SEARCH_API`, `SEARCH_ENGINE_ID`
-   **Vector DB (ChromaDB)**: `CHROMA_PERSIST_PATH`, `CHROMA_COLLECTION`
-   **External APIs**: `NEWS_API_KEY`, `FACT_CHECK_API_KEY`  
-   **Security**: `SECRET_KEY`, `ALGORITHM`, token expiry settings
-   **File Upload**: Size limits, allowed extensions, upload directory

## 🔧 Environment Variables (.env)

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_key

# Google Gemini AI
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-pro
GEMINI_EMBED_MODEL=models/embedding-001
GEMINI_MAX_TOKENS=1000
GEMINI_TEMPERATURE=0.7

# Google Custom Search (for web scraping)
GOOGLE_CUSTOM_SEARCH_API=your_custom_search_api_key
SEARCH_ENGINE_ID=your_search_engine_id

# ChromaDB Vector Database
CHROMA_PERSIST_PATH=.chroma
CHROMA_COLLECTION=verification_docs

# External APIs (optional)
NEWS_API_KEY=your_news_api_key
FACT_CHECK_API_KEY=your_fact_check_api_key

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🧪 Testing

```bash
pytest
```

## 👥 Team Contributions

This project was developed collaboratively by:

### **Dhruv Pokhriyal**
- **Configuration System**: Implemented comprehensive settings management in `app/core/config.py`
- **Environment Setup**: Created structured configuration for Supabase, Gemini AI, and vector database
- **Security Settings**: Developed authentication and authorization configuration

### **Ankit Sinha** 
- **Web Scraping**: Built the web scraping functionality in `app/agents/scraper_agent/web_scraper.py`
- **Content Extraction**: Implemented article extraction and content processing from various sources
- **Data Processing**: Created scraper result models and content parsing logic

### **Karthik** (Team Collaboration)
- **Verification Service**: Collaborated on business logic implementation in `app/services/verification_service.py`
- **RAG Pipeline Integration**: Coordinated between scraping and AI verification components
- **System Architecture**: Contributed to overall verification workflow design

### **Team Collaboration (All Members)**
- **Testing Framework**: Comprehensive test suite development in `tests/`
- **API Design**: FastAPI endpoint design and implementation
- **Documentation**: README and code documentation
- **Integration Testing**: End-to-end testing and system validation

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI       │    │  Verification    │    │   External      │
│   Router        │────│     Service      │────│   Services      │
│                 │    │                  │    │                 │
├─── Posts        │    ├─ Search Agent    │    ├─ Google Search  │
├─── Auth         │    ├─ Web Scraper     │    ├─ News APIs      │
├─── Storage      │    ├─ RAG Pipeline    │    └─ Fact Checkers │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Supabase      │    │    AI/ML Stack   │    │   Vector DB     │
│                 │    │                  │    │                 │
├─ Database       │    ├─ Google Gemini   │    ├─ ChromaDB       │
├─ Auth           │    ├─ Embeddings      │    ├─ Vector Search  │
├─ Storage        │    └─ Content Analysis │    └─ Document Store │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```
