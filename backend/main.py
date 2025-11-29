from fastapi import FastAPI
from app.routes.ingest import router as ingest_router
from app.routes.upload import router as upload_router
from app.routes.search import router as search_router
from app.routes.logs import router as logs_router

app = FastAPI(title = "Log Management Backend (FastAPI)")

# Register routes
app.include_router(ingest_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(logs_router, prefix="/logs")

@app.get("/")
def root():
    return{"status" : "Log Management Backend is running."}