# 🐝 Hive Backend

A Reddit-like application backend with an intelligent verification system powered by web scraping and LangChain RAG pipeline.

## 📖 Project Description

Hive is a Reddit-like social media platform that includes an advanced content verification system. The backend is built with FastAPI and features:

-   **Content Verification**: Automated fact-checking using web scraping and AI
-   **RAG Pipeline**: LangChain-powered retrieval-augmented generation for content analysis
-   **Modern API**: FastAPI-based RESTful API with automatic documentation
-   **Scalable Architecture**: Modular design for easy maintenance and scaling

## 📂 Folder Structure

```
hive-backend/
├── app/                    # Main application package
│   ├── main.py            # FastAPI entry point with health routes
│   ├── api/               # API routes and endpoints
│   │   ├── __init__.py
│   │   └── routes.py      # TODO: API route implementations
│   ├── core/              # Configuration and settings
│   │   ├── __init__.py
│   │   └── config.py      # TODO: App configuration
│   ├── models/            # Data models and schemas
│   │   ├── __init__.py
│   │   └── schemas.py     # TODO: Pydantic models
│   ├── services/          # Business logic layer
│   │   ├── __init__.py
│   │   ├── post_service.py        # TODO: Post operations
│   │   └── verification_service.py # TODO: Verification logic
│   ├── agents/            # Agents responsible for key workflows
│   │   ├── __init__.py
│   │   ├── search_agent/          # Search agent package
│   │   │   └── __init__.py
│   │   ├── scrapper_agent/        # Scrapper agent package
│   │   │   └── __init__.py
│   │   └── rag_agent/             # RAG agent package
│   │       ├── __init__.py
│   │       └── verification_pipeline.py # LangChain RAG pipeline implementation
│   ├── scrapers/          # Web scraping module
│   │   ├── __init__.py
│   │   └── web_scraper.py # TODO: Web scraping implementation
│   └── utils/             # Helper utilities
│       ├── __init__.py
│       └── helpers.py     # TODO: Utility functions
├── tests/                 # Test suite
│   ├── __init__.py
│   └── test_main.py       # TODO: Test implementations
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
└── venv/                 # Virtual environment (created by user)
```

## ⚙️ Setup & Installation

### Prerequisites

-   Python 3.8 or higher
-   pip (Python package installer)

### Environment Setup

1. **Clone the repository**

    ```bash
    git clone <repository-url>
    cd hive-backend
    ```

2. **Create virtual environment**

    ```bash
    python3 -m venv venv
    ```

3. **Activate virtual environment**

    ```bash
    # On macOS/Linux:
    source venv/bin/activate

    # On Windows:
    venv\Scripts\activate
    ```

4. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

## ▶️ Running the Server

### Development Mode

```bash
# Make sure virtual environment is activated
uvicorn app.main:app --reload
```

The server will start at `http://localhost:8000`

### API Documentation

-   **Swagger UI**: `http://localhost:8000/docs`
-   **ReDoc**: `http://localhost:8000/redoc`

### Health Check

-   **Health endpoint**: `http://localhost:8000/health`
-   **Configuration test**: `http://localhost:8000/config/test`

## 🔄 Verification Flow

The content verification system follows this high-level flow:

1. **Content Submission**: User submits a post to the platform
2. **Web Scraping**: System scrapes relevant sources for fact-checking
3. **RAG Pipeline**: LangChain processes scraped data and post content
4. **Classification**: AI classifies the post as verified/unverified/misleading
5. **Result Storage**: Verification results are stored and displayed

### Components:

-   **Scrapers**: Extract information from news sites, fact-checking sources
-   **RAG Pipeline**: LangChain-based retrieval and generation for content analysis
-   **Verification Service**: Business logic for processing and storing results

## 🚀 Next Steps

### Team Assignments:

**🧑‍💻 Dhruv Pokhriyal**

-   **Primary**: RAG Pipeline (`app/agents/rag_agent/verification_pipeline.py`)
-   **Secondary**: Authentication system and API endpoints (helping Karthik)
-   **Collaboration**: Verification service and utilities

**🧑‍💻 Ankit Sinha**

-   **Primary**: Web Scraping (`app/scrapers/web_scraper.py`)
-   **Secondary**: Verification service coordination
-   **Collaboration**: Integration with RAG pipeline

**🧑‍💻 Karthik**

-   **Primary**: API Endpoints (`app/api/routes.py`)
-   **Secondary**: Post service and business logic
-   **Collaboration**: All team members for integration

### Immediate Tasks:

1. **Implement API Routes** (`app/api/routes.py`) - **ASSIGNED TO: Karthik (with Dhruv's help for auth)**

    - User authentication endpoints
    - Post CRUD operations
    - Community management
    - Verification endpoints

2. **Configure Settings** (`app/core/config.py`) - **ASSIGNED TO: Team collaboration**

    - Database configuration
    - API keys and environment variables
    - Application settings

3. **Create Data Models** (`app/models/schemas.py`) - **ASSIGNED TO: Team collaboration**
    - User, Post, Community schemas
    - Verification result models
    - API request/response models

### Core Features:

4. **Web Scraping** (`app/scrapers/web_scraper.py`) - **ASSIGNED TO: Ankit Sinha**

    - Implement scraping logic for fact-checking sources
    - Handle different content types and sources
    - Error handling and rate limiting

5. **RAG Pipeline** (`app/agents/rag_agent/verification_pipeline.py`) - **ASSIGNED TO: Dhruv Pokhriyal**

    - LangChain document retrieval
    - Question-answering system
    - Content classification logic

6. **Business Logic** (`app/services/`) - **ASSIGNED TO: Team collaboration**
    - Post service implementation
    - Verification service logic
    - User management services

### Testing:

7. **Test Suite** (`tests/`) - **ASSIGNED TO: Team collaboration**
    - Unit tests for all components
    - Integration tests for API endpoints
    - Mock tests for external services

## 🛠️ Development

### Code Style

-   Follow PEP 8 guidelines
-   Use type hints where applicable
-   Document functions and classes

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

### Environment Variables

1. **Set up environment (recommended):**

    ```bash
    python setup_env.py
    ```

    **Or manually copy the template:**

    ```bash
    cp env.example .env
    ```

2. **Configure your environment variables in `.env`:**

    ```env
    # Supabase Configuration (Required)
    SUPABASE_URL=https://your-project-id.supabase.co
    SUPABASE_ANON_KEY=your-supabase-anon-key
    SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

    # OpenAI API (Required for RAG Pipeline)
    OPENAI_API_KEY=your-openai-api-key

    # Security (Required)
    SECRET_KEY=your-secret-key

    # Optional: External APIs
    NEWS_API_KEY=your-news-api-key
    FACT_CHECK_API_KEY=your-fact-check-api-key
    ```

3. **Get your Supabase credentials:**

    - Go to [Supabase Dashboard](https://supabase.com/dashboard)
    - Create a new project or select existing one
    - Go to Settings → API
    - Copy the Project URL and API keys

4. **Get your OpenAI API key:**

    - Go to [OpenAI Platform](https://platform.openai.com/api-keys)
    - Create a new API key
    - Copy the key to your `.env` file

<!-- ## 📝 License

[Add your license information here] -->

<!-- ## 🤝 Contributing

[Add contribution guidelines here] -->
