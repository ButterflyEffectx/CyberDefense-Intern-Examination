from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from app.opensearch_client import get_client
from app.auth import decode_token, TokenData

router = APIRouter()


# -----------------------------
# Request Model (Phase 5)
# -----------------------------
class TimeRange(BaseModel):
    from_ts: Optional[str] = None
    to_ts: Optional[str] = None


class Filters(BaseModel):
    source: Optional[str] = None
    event_type: Optional[str] = None
    event_subtype: Optional[str] = None
    severity: Optional[int] = None
    user: Optional[str] = None
    host: Optional[str] = None
    action: Optional[str] = None
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None


class SearchRequest(BaseModel):
    query: Optional[str] = None
    filters: Optional[Filters] = None
    time_range: Optional[TimeRange] = None
    tenant: Optional[str] = None       # admin can override
    size: int = 100
    search_after: Optional[List[Any]] = None
    aggs: bool = False                 # ถ้าอยากขอ dashboard data


# -----------------------------
# Search Route
# -----------------------------
@router.post("/search")
async def search_logs(req: SearchRequest, token: TokenData = Depends(decode_token)):
    client = get_client()

    # -----------------------------
    # Determine Tenant Access
    # -----------------------------
    tenant = token.tenant

    if token.role == "admin" and req.tenant:
        tenant = req.tenant

    index_pattern = f"logs-{tenant.lower()}*"

    # -----------------------------
    # Bool Query Structure
    # -----------------------------
    must = []
    filter_q = []

    # Full-text search
    if req.query:
        must.append({
            "query_string": {
                "query": req.query,
                "fields": [
                    "event_type",
                    "event_subtype",
                    "source",
                    "user",
                    "host",
                    "action",
                    "src_ip",
                    "dst_ip",
                    "raw"
                ]
            }
        })

    # Filters
    if req.filters:
        f = req.filters

        def add_filter(field, value):
            if value is not None:
                filter_q.append({"term": {field: value}})

        add_filter("source", f.source)
        add_filter("event_type", f.event_type)
        add_filter("event_subtype", f.event_subtype)
        add_filter("severity", f.severity)
        add_filter("user", f.user)
        add_filter("host", f.host)
        add_filter("action", f.action)
        add_filter("src_ip", f.src_ip)
        add_filter("dst_ip", f.dst_ip)

    # Time Range
    if req.time_range and (req.time_range.from_ts or req.time_range.to_ts):
        rng = {"range": {"@timestamp": {}}}
        if req.time_range.from_ts:
            rng["range"]["@timestamp"]["gte"] = req.time_range.from_ts
        if req.time_range.to_ts:
            rng["range"]["@timestamp"]["lte"] = req.time_range.to_ts
        filter_q.append(rng)

    # -----------------------------
    # Final Query Body
    # -----------------------------
    query_body = {
        "query": {
            "bool": {
                "must": must if must else [{"match_all": {}}],
                "filter": filter_q
            }
        },
        "size": req.size,
        "sort": [
            {"@timestamp": "desc"},
            {"_id": "desc"}
        ]
    }

    # Pagination
    if req.search_after:
        query_body["search_after"] = req.search_after

    # Aggregations (for dashboard)
    if req.aggs:
        query_body["aggs"] = {
            "by_severity": {"terms": {"field": "severity"}},
            "by_event_type": {"terms": {"field": "event_type"}},
            "by_source": {"terms": {"field": "source"}},
            "timeline": {
                "date_histogram": {
                    "field": "@timestamp",
                    "calendar_interval": "1h"
                }
            }
        }

    # -----------------------------
    # Execute Search
    # -----------------------------
    try:
        resp = client.search(
            index=index_pattern,
            body=query_body
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return resp
