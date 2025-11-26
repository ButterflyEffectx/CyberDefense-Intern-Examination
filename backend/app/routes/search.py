from fastapi import APIRouter, Query, Depends
from app.opensearch_client import get_client
from app.auth import decode_token, TokenData

router = APIRouter()

@router.get("/search")
async def search_logs(
    q: str = Query("*"),
    from_ts: str = Query(None),
    to_ts: str = Query(None),
    tenant_param: str = Query(None),
    token: TokenData = Depends(decode_token)
):
    client = get_client()
    tenant = token.tenant
    if token.role == "admin" and tenant_param:
        tenant = tenant_param
        
    index_pattern  = f"logs-{tenant.lower()}*"
    
    query_body = {
        "query": {
            "query_string": {
                "query": q,
                "fields": ["event_type", "sub", "user", "role", "src_ip"]
            }
        }
    }
    
    if from_ts or to_ts:
        range_q = {"range": {"@timestamp": {}}}
        if from_ts:
            range_q["range"]["@timestamp"]["gte"] = from_ts
        if to_ts:
            range_q["range"]["@timestamp"]["lte"] = to_ts
        query_body["query"] = {
            "bool": {
                "must": query_body["query"],
                "filter": range_q
            }
        }
    
    resp = client.search(
        index = index_pattern,
        body = query_body,
        size = 100
    )
    return resp
    