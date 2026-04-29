from typing import Any

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import settings
from app.models.schemas import StaffRole, StaffUser


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

_VALID_ROLES = {role.value for role in StaffRole}
_DEV_USER = StaffUser(
    id="00000000-0000-0000-0000-000000000002",
    email="dev@local",
    role=StaffRole.CHARGE_NURSE,
)


def _role_value(role: StaffRole | str) -> str:
    return role.value if isinstance(role, StaffRole) else role


def _decode_jwt(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        settings.SUPABASE_JWT_SECRET,
        algorithms=["HS256"],
        audience="authenticated",
    )


def _extract_role(claims: dict[str, Any]) -> StaffRole:
    role = claims.get("app_metadata", {}).get("role", StaffRole.NURSE.value)
    if role not in _VALID_ROLES:
        role = StaffRole.NURSE.value
    return StaffRole(role)


async def get_current_user(token: str | None = Depends(oauth2_scheme)) -> StaffUser:
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


def require_role(*roles: StaffRole | str):
    allowed_roles = {_role_value(role) for role in roles}

    async def guard(user: StaffUser = Depends(get_current_user)) -> StaffUser:
        if _role_value(user.role) not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user

    return guard
