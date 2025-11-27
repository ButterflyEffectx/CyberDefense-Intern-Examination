from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from app.auth import decode_token, TokenData
from app.opensearch_client import get_client

router = APIRouter()

class LogEvent(BaseModel):
    source: str = Field(...)
    event_type: str = Field(...)
    event_subtype: str = Field(...)
    severity: int = Field(...)
    action: str | None = None
    src_ip: str | None = None
    dst_ip: str | None = None
    url: str | None = None
    user: str | None = None
    host: str | None = None
    raw: dict | None = None
    _tags: list[str] | None = None
    timestamp: datetime | None = None


@router.post("/ingest")
async def ingest_log(
    event: LogEvent,
    token: TokenData = Depends(decode_token),
    client=Depends(get_client)
):
    tenant = token.tenant

    today = datetime.utcnow().strftime("%Y.%m.%d")
    index_name = f"logs-{tenant.lower()}-{today}"

    doc = event.dict()
    if not doc.get("timestamp"):
        doc["timestamp"] = datetime.utcnow().isoformat()

    try:
        response = client.index(
            index=index_name,
            body=doc,
            refresh=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "status": "ok",
        "indexed_to": index_name,
        "id": response["_id"]
    }
