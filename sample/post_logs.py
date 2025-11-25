import requests
import json

URL = "http://localhost:8000/api/ingest"

def send_sample():
    payload = {
        "tenant" : "demoA",
        "source" : "api",
        "event_type" : "app_login_failed",
        "user" : "alice",
        "ip" : "203.0.113.7",
        "@timestamp" : "2025-11-25T10:15:30Z"
    }
    r = requests.post(URL, json=payload)
    print("r.status_code, r.text")
    
if __name__ == "__main__":
    send_sample()

