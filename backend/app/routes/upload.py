from fastapi import APIRouter, UploadFile
import json
from app.opensearch_client import get_client
from app.normalization import normalize_log
import uuid

router = APIRouter()

@router.post("/upload")
async def upload_logs(file: UploadFile):
    content = await file.read()
    logs = json.loads(content)
    
    client = get_client()
    
    for entry in logs:
        doc = normalize_log(entry)
        index_name = f"logs-{doc['tenant']}"
        client.index(
            index = index_name,
            body = doc,
            id = str(uuid.uuid4())
        )
    
    return {"status": "ok", "items": len(logs)}