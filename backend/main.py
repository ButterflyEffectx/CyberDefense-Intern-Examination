from fastapi import FastAPI
from app.routes import ingest, upload, search
from app.routes import upload

app = FastAPI(title = "Log Management Backend (FastAPI)")

# Register routes
app.include_router(ingest.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(search.router, prefix="/api")

@app.get("/")
def root():
    return{"status" : "Log Management Backend is running."}