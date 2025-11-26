from fastapi import APIRouter, UploadFile, File, Depends
import json
from app.opensearch_client import get_client
from app.normalization import normalize_log
from app.auth import decode_token, TokenData
import uuid

router = APIRouter()

@router.post("/upload")
async def upload_logs(file: UploadFile = File(...), token: TokenData = Depends(decode_token)):
    content = await file.read()
    try:
        logs = json.loads(content)
    except Exception as e:
        return {"status": "error", "message": "Invalid JSON file", "error": str(e)}
    
    client = get_client()
    count = 0
    for entry in logs:
        doc = normalize_log(entry)
        doc["tenant"] = token.tenant
        doc["sub"] = token.sub
        doc["role"] = token.role
        index_name = f"logs-{doc['tenant'].lower()}"
        client.index(
            index = index_name,
            body = doc,
            id = str(uuid.uuid4())
        )
        count += 1
    
    return {"status": "ok", "items": count}