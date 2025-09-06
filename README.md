# 🐝 Hive Backend

A Reddit-like backend with content verification powered by web scraping and a Gemini-based RAG pipeline.

## 📖 Project Description

Hive provides a FastAPI backend for posts, media storage, and user auth (Supabase), with automatic verification of post content via a RAG pipeline.

## 📂 Folder Structure

```
Hive_Backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routers/
│   │       ├── posts.py           # posts CRUD, reactions, listing
│   │       ├── storage.py               # uploads to Supabase Storage
│   │       └── auth.py             # Supabase OAuth, JWT auth helpers
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py                    # settings (Supabase, Gemini, Chroma, etc.)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── rag.py                       # RagRequest/Response enums
│   │   ├── post.py                   # User, Post, Comment, ShowPost, tokens
│   │   └── scraper.py                   # ScraperResult
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── scrapers/
│   │   │   └── scraper_agent/web_scraper.py
│   │   ├── search_agent/
│   │   │   └── search_agent.py
│   │   └── rag_agent/
│   │       └── rag_agent.py             # Gemini + Chroma pipeline
│   ├── services/
│   │   ├── __init__.py
│   │   └── verification_service.py      # verification orchestration
│   └── utils/
│       ├── __init__.py
│       └── supabase_client.py           # client factory (anon/admin)
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   └── test_supabase_client.py
├── pyproject.toml | poetry.lock | requirements.txt
├── setup_env.py | env.example | README.md
└── venv/
```

## ⚙️ Setup & Installation

### Prerequisites

-   Python 3.13+
-   Supabase project (URL + anon + service role keys)

### Environment Setup

1. Create and activate a virtual environment + install redis (recommended)

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    sudo apt-get install redis-server
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
sudo service redis-server start
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

-   POST `/` → create post (body: `Post`), enqueues verification
-   GET `/` → list all posts
-   GET `/users/{uid}/posts` → list posts by user
-   GET `/{pid}` → get one post
-   PUT `/{pid}` → update post (owner only)
-   DELETE `/{pid}` → delete post (owner only)
-   POST `/{pid}/like` → increment likes
-   POST `/{pid}/dislike` → increment dislikes

## 🧠 Verification Pipeline

-   Orchestrated in `app/services/verification_service.py` using:
    -   `search_agent.get_links` to find sources
    -   `scraper_agent.WebScraper` to fetch content
    -   `VerificationRAGPipeline` (Gemini + Chroma) to verify/classify

`VerificationRAGPipeline.verify(RagRequest)` returns:

```json
{
    "status": "verified | unverified | personal_opinion | misinformation | factual_error | other",
    "confidence": 0.0,
    "answer": "...",
    "supporting_context": ["..."],
    "rationale": "...",
    "metadata": { "post_id": "..." }
}
```

## 🧱 Models (Pydantic)

-   `app/models/schemas.py`
    -   `User`, `Post`, `Comment`, `ShowPost`, `Token`, `TokenData`
    -   `PostContentRequest`, `PostVerificationRequest`
-   `app/models/rag.py`
    -   `RagRequest`, `RagResponse`
-   `app/models/scraper.py`
    -   `ScraperResult`

## 🛠️ Configuration

`app/core/config.py` exposes `settings` with nested sections:

-   Supabase: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
-   Gemini: `GEMINI_API_KEY`, `GEMINI_MODEL`, `GEMINI_EMBED_MODEL`, `GEMINI_MAX_TOKENS`, `GEMINI_TEMPERATURE`, `GOOGLE_CUSTOM_SEARCH_API`, `SEARCH_ENGINE_ID`
-   Vector DB (Chroma): `CHROMA_PERSIST_PATH`, `CHROMA_COLLECTION`
-   API: `NEWS_API_KEY`, `FACT_CHECK_API_KEY`
-   Security: `SECRET_KEY`, `ALGORITHM`, token expiries

## 🔧 Environment Variables (.env)

```env
# Supabase
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...

# Gemini
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-pro
GEMINI_EMBED_MODEL=models/embedding-001
GEMINI_MAX_TOKENS=1000
GEMINI_TEMPERATURE=0.7
GOOGLE_CUSTOM_SEARCH_API=...
SEARCH_ENGINE_ID=...

# Chroma
CHROMA_PERSIST_PATH=.chroma
CHROMA_COLLECTION=verification_docs

# API
NEWS_API_KEY=...
FACT_CHECK_API_KEY=...

# Security
SECRET_KEY=change-me
```

## 🧪 Testing

```bash
pytest
```

## 📄 Notes

-   Uses Redis + RQ for async verification task enqueue from post creation.
-   Supabase client is centralized in `app/utils/supabase_client.py`.
