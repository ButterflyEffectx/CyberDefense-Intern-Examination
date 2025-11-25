from fastapi import APIRouter
from app.opensearch_client import get_client
from app.normalization import normalize_log
import uuid

router = APIRouter()

@router.post("/ingest")
async def ingest_log(data: dict):
    client = get_client()
    
    doc = normalize_log(data)
    index_name = f"logs-{doc['tenant']}"
    
    client.index(
        index = index_name,
        body = doc,
        id = str (uuid.uuid4())
    )
    
    return {"status" : "ok", "indexed" : True}
    