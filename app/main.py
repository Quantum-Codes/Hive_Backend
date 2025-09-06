from fastapi import APIRouter, FastAPI
from app.api.routers import posts, storage, auth
from app.core.config import settings, is_development

routes = [
    posts.router,
    storage.router,
    auth.router
]

app = FastAPI(
    title=settings.app_name,
    description="A Reddit-like app with verification system",
    version=settings.app_version,
    debug=settings.debug
)


for route in routes:
    app.include_router(route)

@app.get("/")
async def root():
    return {"message": "Welcome to Hive Backend"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "hive-backend"}

@app.get("/config/test")
async def test_config():
    """Test endpoint to verify configuration is working."""
    return {
        "app_name": settings.app_name,
        "environment": settings.environment,
        "debug": settings.debug,
        "supabase_configured": bool(settings.supabase.url and settings.supabase.anon_key),
        "gemini_configured": bool(settings.gemini.api_key),
    }
