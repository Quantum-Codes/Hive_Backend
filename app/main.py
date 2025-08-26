from fastapi import FastAPI

app = FastAPI(
    title="Hive Backend",
    description="A Reddit-like app with verification system",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to Hive Backend"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "hive-backend"}
