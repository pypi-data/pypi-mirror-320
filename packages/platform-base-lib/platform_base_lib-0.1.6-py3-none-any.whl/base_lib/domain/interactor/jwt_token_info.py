from pydantic import BaseModel
from typing import Optional


class JWTTokenInfo(BaseModel):
    userId: str
    organizationId: str
    externalUserId: Optional[str]
    authType: str
    exp: int
    iat: int
