from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.core.config import settings
from app.models.schemas import StaffUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

_VALID_ROLES = {"nurse", "charge_nurse", "admin"}
_DEV_USER = StaffUser(id="dev", email="dev@local", role="charge_nurse")


# T-06: decode and verify a Supabase-issued JWT
def _decode_jwt(token: str) -> dict:
    return jwt.decode(
        token,
        settings.SUPABASE_JWT_SECRET,
        algorithms=["HS256"],
        audience="authenticated",
    )


# T-07: extract custom role from app_metadata claim
def _extract_role(claims: dict) -> str:
    role = claims.get("app_metadata", {}).get("role", "nurse")
    return role if role in _VALID_ROLES else "nurse"


# T-08: FastAPI dependency — verifies token and returns StaffUser
async def get_current_user(token: str = Depends(oauth2_scheme)) -> StaffUser:
    # Dev bypass: AUTH_ENABLED=false or no JWT secret configured
    if not settings.AUTH_ENABLED or not settings.SUPABASE_JWT_SECRET:
        return _DEV_USER

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        claims = _decode_jwt(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return StaffUser(
        id=claims.get("sub", ""),
        email=claims.get("email", ""),
        role=_extract_role(claims),
    )
