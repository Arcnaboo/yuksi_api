from typing import Dict, Any
from app.services import user_service


async def register(
    email: str,
    password: str,
    phone: str,
    first_name: str,
    last_name: str
) -> Dict[str, Any]:
    result = await user_service.register_user(
        email, password, phone, first_name, last_name
    )
    
    if not result:
        return {
            "success": False,
            "message": "Email already registered or Default role not found",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "User registered successfully",
        "data": result
    }


async def login(email: str, password: str) -> Dict[str, Any]:
    result = await user_service.login_user(email, password)
    
    if not result:
        return {
            "success": False,
            "message": "Wrong email or password",
            "data": {}
        }
    
    if result == "banned":
        return {
            "success": False,
            "message": "User is deleted or inactive",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Login successful",
        "data": result
    }

