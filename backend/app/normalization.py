from datetime import datetime
from typing import Optional

DEFAULT_SCHEMA = [
    "@timestamp", "tenant", "source", "event_type", "event_subtype", "severity",
    "action", "src_ip", "src_port", "dst_ip", "dst_port", "protocol", "sub", "user",
    "role", "host", "process", "url", "http_method", "status_code", "rule_name", "rule_id",
    "cloud", "raw", "_tags"
]

def normalize_log(data: dict, token: Optional[dict] = None) -> dict:
    
    ts = data.get("@timestamp") or data.get("timestamp")
    if not ts:
        timestamp = datetime.utcnow().isoformat() + "Z"
    
    tenant = data.get("tenant") or (token.get("tenant") if token else os_default_tenant())
    sub = data.get("sub") or (token.get("sub") if token else None)
    role = data.get("role") or (token.get("role") if token else None)
    
    normalized = {
        "@timestamp": ts,
        "tenant": tenant,
        "source": data.get("source", data.get("vendor", "unknown")),
        "event_type": data.get("event_type", data.get("event", "unknown")),
        "event_subtype": data.get("event_subtype"),
        "severity": data.get("severity"),
        "action": data.get("action"),
        "src_ip": data.get("src_ip") or data.get("ip") or data.get("src"),
        "src_port": data.get("src_port"),
        "dst_ip": data.get("dst_ip"),
        "dst_port": data.get("dst_port"),
        "protocol": data.get("protocol"),
        "sub": sub,
        "role": role,
        "host": data.get("host"),
        "process": data.get("process"),
        "url": data.get("url"),
        "http_method": data.get("http_method"),
        "status_code": data.get("status_code"),
        "rule_name": data.get("rule_name"),
        "rule_id": data.get("rule_id"),
        "cloud": data.get("cloud", {}),
        "raw": data,
        "_tags": data.get("_tags", []),
    }
    return normalized 

def os_default_tenant():
    import os
    return os.getenv("DEFAULT_TENANT", "demoA")  