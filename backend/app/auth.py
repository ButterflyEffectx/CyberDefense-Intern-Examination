from fastapi import APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
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
        raise HTTPException(status_code=401, detail="Invalid token")