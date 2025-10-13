from fastapi import APIRouter, Path, Body
from ..models.courier_model import (
    CourierRegisterStep1Req,
    CourierRegisterStep2Req,
    CourierRegisterStep3Req,
)
from ..controllers import courier_controller as ctrl

router = APIRouter(
    prefix="/api/Courier",
    tags=["Courier"],
)

@router.post(
    "/register1",
    summary="Courier Register Step 1",
    description="Telefon, ad-soyad, e-posta ve sözleşme onayı ile kullanıcıyı başlatır.",
    responses={
        200: {
            "description": "Kayıt adım 1 tamam.",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Başarılı örnek",
                            "value": {
                                "success": True,
                                "message": "CourierRegister step1 completed",
                                "data": {"userId": "6aef8f5c-27e0-4e8c-8b2d-36a78b6a0b0a"}
                            }
                        },
                        "already_exists": {
                            "summary": "Zaten kayıtlı",
                            "value": {
                                "success": False,
                                "message": "Email or phone already registered",
                                "data": {}
                            }
                        }
                    }
                }
            },
        }
    },
)
def courier_register1(
    req: CourierRegisterStep1Req = Body(
        ...,
        examples={
            "valid": {
                "summary": "Geçerli istek",
                "value": {
                    "phone": "5551112233",
                    "firstName": "Ahmet",
                    "lastName": "Yüksel",
                    "email": "ahmet@yuksi.com",
                    "password": "secret123",
                    "confirmPassword": "secret123",
                    "confirmContract": True,
                    "countryId": 90
                },
            },
            "password_mismatch": {
                "summary": "Parola eşleşmiyor",
                "value": {
                    "phone": "5551112233",
                    "firstName": "Ahmet",
                    "lastName": "Yüksel",
                    "email": "ahmet@yuksi.com",
                    "password": "secret123",
                    "confirmPassword": "secretXYZ",
                    "confirmContract": True,
                    "countryId": 90
                },
            },
            "contract_not_confirmed": {
                "summary": "Sözleşme onaysız",
                "value": {
                    "phone": "5551112233",
                    "firstName": "Ahmet",
                    "lastName": "Yüksel",
                    "email": "ahmet@yuksi.com",
                    "password": "secret123",
                    "confirmPassword": "secret123",
                    "confirmContract": False,
                    "countryId": 90
                },
            },
        },
    )
):
    return ctrl.courier_register1(req)


@router.post(
    "/users/{user_id}/register2",
    summary="Courier Register Step 2",
    description="Kullanıcının çalışma tipini tanımlar.",
    responses={
        200: {
            "description": "Kayıt adım 2 tamam.",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Başarılı",
                            "value": {
                                "success": True,
                                "message": "CourierRegister step2 completed",
                                "data": {"userId": "6aef8f5c-27e0-4e8c-8b2d-36a78b6a0b0a"}
                            }
                        },
                        "not_found": {
                            "summary": "Kullanıcı yok",
                            "value": {
                                "success": False,
                                "message": "User not found",
                                "data": {}
                            }
                        }
                    }
                }
            },
        }
    },
)
def courier_register2(
    user_id: str = Path(..., description="Kullanıcının UUID değeri"),
    req: CourierRegisterStep2Req = Body(
        ...,
        examples={
            "working_courier": {"summary": "Kurye çalışma tipi", "value": {"workingType": 1}},
            "part_time": {"summary": "Part-time", "value": {"workingType": 2}},
        },
    ),
):
    return ctrl.courier_register2(user_id, req)


@router.post(
    "/users/{user_id}/register3",
    summary="Courier Register Step 3",
    description="Araç ve bölge bilgilerini kaydeder, akışı tamamlar.",
    responses={
        200: {
            "description": "Kayıt adım 3 tamam.",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Başarılı",
                            "value": {
                                "success": True,
                                "message": "CourierRegister step3 completed",
                                "data": {"userId": "6aef8f5c-27e0-4e8c-8b2d-36a78b6a0b0a"}
                            }
                        },
                        "not_found": {
                            "summary": "Kullanıcı yok",
                            "value": {
                                "success": False,
                                "message": "User not found",
                                "data": {}
                            }
                        }
                    }
                }
            },
        }
    },
)
def courier_register3(
    user_id: str = Path(..., description="Kullanıcının UUID değeri"),
    req: CourierRegisterStep3Req = Body(...),
):
    return ctrl.courier_register3(user_id, req)


@router.get(
    "/{user_id}/profile",
    summary="Get Courier Profile",
    description="Fetches the profile information of a courier by user ID.",
    responses={
        200: {
            "description": "Courier profile retrieved successfully.",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Successful response",
                            "value": {
                                "success": True,
                                "message": "Courier profile",
                                "data": {
                                    "userId": "6aef8f5c-27e0-4e8c-8b2d-36a78b6a0b0a",
                                    "phone": "5551112233",
                                    "firstName": "Test",
                                    "lastName": "Test",
                                    "email": "test@test.com",
                                    "createdAt": "2023-10-01T12:34:56Z",
                                    "countryId": 90,
                                    "countryName": "Turkey",
                                    "stateId": 34,
                                    "stateName": "Istanbul",
                                    "workingType": 1,
                                    "vehicleType": 0,
                                    "vehicleCapacity": 100,
                                    "vehicleYear": 2020
                                }
                            }
                        },
                        "not_found": {
                            "summary": "Courier not found",
                            "value": {
                                "success": False,
                                "message": "Courier not found",
                                "data": {}
                            }
                        }
                    }
                }
            },
        }
    },
)
def get_courier_profile(
    user_id: str = Path(..., description="The UUID of the courier user"),
):
    return ctrl.get_courier_profile(user_id)


@router.get("/list",
    summary="Get Courier List",
    description="Fetches the profile information of a courier by user ID.",
    responses={
        200: {
            "description": "Courier profile retrieved successfully.",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Successful response",
                            "value": {
                                "success": True,
                                "message": "Courier profile",
                                "data": [{
                                    "userId": "6aef8f5c-27e0-4e8c-8b2d-36a78b6a0b0a",
                                    "phone": "5551112233",
                                    "firstName": "Test",
                                    "lastName": "Test",
                                    "email": "test@test.com",
                                    "createdAt": "2023-10-01T12:34:56Z",
                                    "countryId": 90,
                                    "countryName": "Turkey",
                                    "stateId": 34,
                                    "stateName": "Istanbul",
                                    "workingType": 1,
                                    "vehicleType": 0,
                                    "vehicleCapacity": 100,
                                    "vehicleYear": 2020
                                }]
                            }
                        },
                        "not_found": {
                            "summary": "Courier not found",
                            "value": {
                                "success": False,
                                "message": "Courier not found",
                                "data": {}
                            }
                        }
                    }
                }
            },
        }
    },
)
def list_couriers():
    return ctrl.list_couriers()