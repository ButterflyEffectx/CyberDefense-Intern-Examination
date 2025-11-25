from datetime import datetime

def normalize_log(data: dict):
    # handle missing fields
    timestamp = data.get("@timestamp") or datetime.utcnow().isoformat() + "Z"
    
    return {
        "@timestamp": timestamp,
        "tenant": data.get("tenant", "default"),
        "source": data.get("source", "unknown"),
        "event_type": data.get("event_type", "unknown"),
        "user": data.get("user"),
        "ip" : data.get("ip"),
        "raw":data
    }   