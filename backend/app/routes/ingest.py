from fastapi import APIRouter, Depends
from app.auth import decode_token, TokenData
from app.opensearch_client import get_client
from app.normalization import normalize_log
import uuid

router = APIRouter()

@router.post("/ingest")
async def ingest_log(data: dict, token: TokenData =Depends(decode_token)):
    client = get_client()
    
    doc = normalize_log(data)
    doc["tenant"] = token.tenant
    index_name = f"logs-{doc['tenant']}"
    
    resp = client.index(
        index = index_name,
        body = doc,
        id = str (uuid.uuid4())
    )
    
    return {"status" : "ok", "result" : resp.get("result")}
    