from fastapi import APIRouter, Query
from app.opensearch_client import get_client

router = APIRouter()

@router.get("/search")
async def search_logs(
    tenant: str,
    query: str = "*"
):
    client = get_client()
    index_pattern  = f"logs-{tenant}*"
    
    result = client.search(
        index = index_pattern,
        body = {
            "query": {
                "query_string": {"query": query}
            }
        }
    )
    return result
    