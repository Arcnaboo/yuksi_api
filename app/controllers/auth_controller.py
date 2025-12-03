from fastapi import Depends, HTTPException, status, status,Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..utils.security import decode_jwt
from ..services import auth_service
from ..services import support_permission_service as support_perm_svc

http_bearer = HTTPBearer(auto_error=False)

def require_roles(allowed: list[str]):
    def _dep(credentials: HTTPAuthorizationCredentials = Security(http_bearer)):
        if not credentials or not credentials.credentials:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
        token = credentials.credentials
        payload = decode_jwt(token)
        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

        roles = payload.get("role") or payload.get("roles") or []
        if isinstance(roles, str):
            roles = [roles]

        if not any(r in roles for r in allowed):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: insufficient role")
        return payload
    return _dep

async def register(first_name: str, last_name:str, email: str, phone: str, password: str):
    tokens = await auth_service.register(first_name,last_name, email, phone, password)
    if not tokens:
        return {"success": False, "message": "Email or phone already registered", "data": {}}
    return {"success": True, "message": "Driver registered", "data": tokens}

async def login(email: str, password: str):
    tokens = await auth_service.login(email, password)
    if not tokens:
        return {"success": False, "message": "Wrong email or password", "data": {}}
    elif tokens == "banned":
        return {"success": False, "message": "User is deleted", "data": {}}
    return {"success": True, "message": "Login successful", "data": tokens}

async def get_current_driver(credentials: HTTPAuthorizationCredentials = Security(http_bearer)):
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = credentials.credentials
    payload = decode_jwt(token)  
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    driver_id = payload.get("sub")
    driver = await auth_service.get_driver(driver_id)
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return driver


async def refresh(refresh_token: str):
    tokens = await auth_service.refresh_with_token(refresh_token)
    if not tokens:
        return {"success": False, "message": "Invalid refresh token", "data": {}}
    elif tokens == "banned":
        return {"success": False, "message": "User is deleted", "data": {}}
    return {"success": True, "message": "Token refreshed", "data": tokens}


async def logout(refresh_token: str):
    ok = await auth_service.revoke_refresh_token(refresh_token)
    if not ok:
        return {"success": False, "message": "Refresh token already invalid or not found", "data": {}}
    return {"success": True, "message": "Logged out", "data": {}}


def require_support_module(module_number: int):
    """
    Support kullanıcısının belirli bir modüle erişim yetkisi var mı kontrol eder.
    
    Args:
        module_number: Modül numarası (1-7)
            - 1: Kuryeler
            - 2: Yükler (Bayiler, Kurumsal, Bireysel)
            - 3: Restoranlar
            - 4: Ödemeler
            - 5: Taşıyıcılar
            - 6: Siparişler
            - 7: Ticari kısım
    
    Returns:
        Async dependency function that checks module access
    """
    async def _dep(credentials: HTTPAuthorizationCredentials = Security(http_bearer)):
        if not credentials or not credentials.credentials:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
        token = credentials.credentials
        payload = decode_jwt(token)
        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

        # Support rolü kontrolü
        roles = payload.get("role") or payload.get("roles") or []
        if isinstance(roles, str):
            roles = [roles]
        
        if "Support" not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu endpoint'e sadece Support kullanıcıları erişebilir"
            )
        
        # Support kullanıcı ID'si
        support_user_id = payload.get("userId") or payload.get("sub")
        if not support_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token'da kullanıcı ID bulunamadı"
            )
        
        # Modül yetkisi kontrolü (async)
        has_permission = await support_perm_svc.check_support_module(
            support_user_id=str(support_user_id),
            module_number=module_number
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bu modüle ({module_number}) erişim yetkiniz bulunmamaktadır"
            )
        
        return payload
    
    return _dep
