# setup_appliance.md

เอกสารนี้เป็น "คู่มือติดตั้งโหมด Appliance" สำหรับ Demo Log Management ที่เรากำลังพัฒนา — จะรวมไฟล์ `docker-compose.yml`, `.env.example`, นโยบาย OpenSearch (index template + ILM), สคริปต์ตัวอย่างสำหรับยิง log (post_logs.py, send_syslog.sh), และขั้นตอนรันระบบทีละขั้นแบบสั้น ๆ เพื่อให้กรรมการสามารถทดสอบ acceptance checklist ได้ทันที

---

## เนื้อหาในไฟล์ที่ให้พร้อมใช้

* `docker-compose.yml` — รัน OpenSearch, OpenSearch Dashboards, backend (FastAPI)
* `.env.example` — ค่าตั้งต้นที่ต้องใส่
* `opensearch/ilm_policy.json` — policy สำหรับ retention 7 วัน
* `opensearch/index_template.json` — mapping แบบพื้นฐานสำหรับ logs-<tenant>-YYYY.MM.DD
* `samples/post_logs.py` — ส่ง HTTP POST /api/ingest
* `samples/send_syslog.sh` — ส่ง syslog ผ่าน nc
* `Makefile` — คำสั่งช่วยรันและ seed data

---

## docker-compose.yml

ใช้ไฟล์นี้สำหรับโหมด Appliance (รันบนเครื่อง/VM เดียว)

```yaml
version: "3.8"
services:
  opensearch:
    image: opensearchproject/opensearch:2.10.2
    environment:
      - cluster.name=opensearch-cluster
      - discovery.type=single-node
      - "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m"
      - plugins.security.disabled=true
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - opensearch-data:/usr/share/opensearch/data
    ports:
      - "9200:9200"
      - "9600:9600"

  opensearch-dashboards:
    image: opensearchproject/opensearch-dashboards:2.10.2
    ports:
      - "5601:5601"
    depends_on:
      - opensearch

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OPENSEARCH_HOST=opensearch
      - OPENSEARCH_PORT=9200
      - SECRET_KEY=changemeverystrongsecret
    depends_on:
      - opensearch

volumes:
  opensearch-data:
```

---

## .env.example

```
OPENSEARCH_HOST=opensearch
OPENSEARCH_PORT=9200
SECRET_KEY=replace_with_strong_random
JWT_ALGORITHM=HS256
DEFAULT_TENANT=demoA
```

---

## OpenSearch ILM policy (opensearch/ilm_policy.json)

Retention ขั้นต่ำ 7 วัน ใช้ ILM แบบง่าย (rollover & delete)

```json
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {"rollover": {"max_age": "1d", "max_size": "50gb"}}
      },
      "delete": {
        "min_age": "7d",
        "actions": {"delete": {}}
      }
    }
  }
}
```

> หมายเหตุ: ใน OpenSearch เวอร์ชันบางรุ่นคำสั่งจัดการ ILM อาจต่างกันเล็กน้อย แต่แนวคิดคือเก็บอย่างน้อย 7 วันแล้วลบ

---

## Index Template (opensearch/index_template.json)

```json
{
  "index_patterns": ["logs-*"],
  "template": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0
    },
    "mappings": {
      "properties": {
        "@timestamp": {"type": "date"},
        "tenant": {"type": "keyword"},
        "source": {"type": "keyword"},
        "event_type": {"type": "keyword"},
        "severity": {"type": "integer"},
        "action": {"type": "keyword"},
        "src_ip": {"type": "ip"},
        "dst_ip": {"type": "ip"},
        "user": {"type": "keyword"},
        "host": {"type": "keyword"},
        "raw": {"type": "object", "enabled": false}
      }
    }
  }
}
```

---

## Backend: AuthN/AuthZ + tenant filter (code snippets)

ปลั๊กอินใน `backend/app` จะประกอบด้วย `auth.py` และ middleware สำหรับตรวจ JWT และผนวก tenant filter ให้อัตโนมัติ

### backend/app/auth.py

```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
import os

security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

class TokenData:
    def __init__(self, sub: str, role: str, tenant: str):
        self.sub = sub
        self.role = role
        self.tenant = tenant


def decode_token(creds: HTTPAuthorizationCredentials = Security(security)) -> TokenData:
    token = creds.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        role = payload.get("role")
        tenant = payload.get("tenant")
        if sub is None or role is None or tenant is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return TokenData(sub=sub, role=role, tenant=tenant)
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
```

### วิธีใช้งานใน route

```python
from fastapi import Depends
from app.auth import decode_token

@router.post("/ingest")
async def ingest_log(data: dict, token=Depends(decode_token)):
    # token.tenant, token.role available
    # ensure tenant matches payload or override based on policy
    doc = normalize_log(data)
    # enforce tenant
    doc["tenant"] = token.tenant
    index_name = f"logs-{doc['tenant']}"
    ...
```

> แนวปฏิบัติ: ถ้ระบบที่ส่ง log เป็น service ที่ไม่มี JWT (เช่น syslog จากอุปกรณ์) ให้ใช้ mapping เช่น header/parameter หรือค่า default tenant (แต่ใน assignment ต้องสามารถให้ผู้ส่งระบุ tenant หรือใช้ script จำลอง)

---

## Sample script: post_logs.py (samples/post_logs.py)

```python
import requests
import json

URL = "http://localhost:8000/api/ingest"

def send_sample():
    payload = {
        "tenant": "demoA",
        "source": "api",
        "event_type": "app_login_failed",
        "user": "alice",
        "ip": "203.0.113.7",
        "@timestamp": "2025-08-20T07:20:00Z"
    }
    r = requests.post(URL, json=payload)
    print(r.status_code, r.text)

if __name__ == '__main__':
    send_sample()
```

## Sample script: send_syslog.sh (samples/send_syslog.sh)

```bash
#!/bin/bash
# send syslog via nc to a local fluent-bit listening on 514
SYSLOG_MSG="<134>Aug 20 12:44:56 fw01 vendor=demo product=ngfw action=deny src=10.0.1.10 dst=8.8.8.8 spt=5353 dpt=53 proto=udp msg=DNS blocked"

# adjust IP/PORT of collector
nc -u 127.0.0.1 514 <<< "$SYSLOG_MSG"
```

---

## Makefile (ช่วยคำสั่ง)

```makefile
.PHONY: up seed post

up:
	docker compose up -d --build

seed:
	python3 samples/post_logs.py

post:
	python3 samples/post_logs.py
```

---

## ขั้นตอนติดตั้ง (Appliance) สรุปสั้น ๆ

1. เตรียมเครื่อง Ubuntu 22.04+, ติดตั้ง Docker & Docker Compose
2. วาง repository โครงงานบนเครื่อง
3. แก้ไฟล์ `.env` จาก `.env.example`
4. รัน `docker compose up -d --build`
5. รอ OpenSearch (9200) และ Dashboards (5601) พร้อม
6. รัน `make seed` เพื่อยิง sample log
7. ตรวจ UI ที่ `http://<host>:5601` หรือเรียก `GET /api/search` เพื่อดูผล

---

## Notes & Troubleshooting

* ถ้า OpenSearch ยังไม่พร้อม backend อาจ connect fail — รอสักครู่และ retry
* ถ้ต้องการ HTTPS สำหรับ SaaS ให้ติดตั้ง reverse-proxy (nginx) กับ cert หรือใช้ self-signed certificate และอธิบายขั้นตอนใน `docs/setup_saas.md`

---

*End of setup_appliance.md*
