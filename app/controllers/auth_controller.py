from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from ..utils.security import decode_jwt
from ..services import auth_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def register(first_name: str, last_name:str, email: str, phone: str, password: str):
    token = auth_service.register(first_name,last_name, email, phone, password)
    if not token:
        return {"success": False, "message": "Email or phone already registered", "data": {}}
    return {"success": True, "message": "Driver registered", "data": {"access_token": token, "token_type": "bearer"}}

def login(email: str, password: str):
    token = auth_service.login(email, password)
    if not token:
        return {"success": False, "message": "Wrong email or password", "data": {}}
    return {"success": True, "message": "Login successful", "data": {"access_token": token, "token_type": "bearer"}}

def get_current_driver(token: str = Depends(oauth2_scheme)):
    payload = decode_jwt(token)
    driver_id = payload.get("sub")
    driver = auth_service.get_driver(driver_id)
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return driver
