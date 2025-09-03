# TODO: Implement tests here
# This file will contain unit and integration tests for the application
# Examples: API endpoint tests, service tests, model tests
#
# ASSIGNED TO: Team collaboration (All members)
# TASK: Implement comprehensive test suite
# - Unit tests for all components
# - Integration tests for API endpoints
# - Mock tests for external services
# - Test coverage for scraping, RAG pipeline, and services
# - Authentication and authorization tests

from fastapi import FastAPI
from app.api.routers import postRoutes,storage,userAuthentication
app = FastAPI()

app.include_router(postRoutes.router)
app.include_router(storage.router)
app.include_router(userAuthentication.router)
