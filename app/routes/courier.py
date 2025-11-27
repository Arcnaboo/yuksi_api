from typing import List
from fastapi import APIRouter, Path, Body, Depends
from fastapi.params import Query
from ..models.courier_model import (
    CourierOrderStatusChangeReq,
    CourierOrderStatusChangeRes,
    CourierRegisterStep1Req,
    CourierRegisterStep2Req,
    CourierRegisterStep3Req,
    CourierProfileUpdateReq,
    CourierHistoryRes
)
from ..controllers import courier_controller as ctrl
from ..controllers import auth_controller
from uuid import UUID

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
async def courier_register1(
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
    return await ctrl.courier_register1(req)


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
async def courier_register2(
    user_id: str = Path(..., description="Kullanıcının UUID değeri"),
    req: CourierRegisterStep2Req = Body(
        ...,
        examples={
            "working_courier": {"summary": "Kurye çalışma tipi", "value": {"workingType": 1}},
            "part_time": {"summary": "Part-time", "value": {"workingType": 2}},
        },
    ),
):
    return await ctrl.courier_register2(user_id, req)


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
async def courier_register3(
    user_id: str = Path(..., description="Kullanıcının UUID değeri"),
    req: CourierRegisterStep3Req = Body(
        ...,
        openapi_examples={
            "with_dealer": {
                "summary": "Bayi ile (dealer_id gönderilir)",
                "value": {
                    "vehicleType": 0,
                    "vehicleCapacity": 100,
                    "stateId": 34,
                    "vehicleYear": 2020,
                    "dealer_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                    "documents": [
                        {"docType": "VergiLevhasi", "fileId": "c9c9e6f4-9db9-4b1a-8f90-7c0f1fb2a4cd"},
                        {"docType": "EhliyetOn",  "fileId": "5b2b1f16-6e87-4f2b-9d9e-1e0b0d0a1f22"},
                        {"docType": "EhliyetArka","fileId": "3a1a2b3c-4d5e-6f70-8g90-1h2i3j4k5l6m"},
                        {"docType": "RuhsatOn",  "fileId": "7n8o9p0q-1r2s-3t4u-5v6w-7x8y9z0a1b2c"},
                        {"docType": "RuhsatArka",  "fileId": "7n8o9p0q-1r2s-3t4u-5v6w-7x8y9z0a1b2c"},
                        {"docType": "KimlikOn","fileId": "d3e4f5g6-h7i8-j9k0-l1m2-n3o4p5q6r7s8"},
                        {"docType": "KimlikArka","fileId": "d3e4f5g6-h7i8-j9k0-l1m2-n3o4p5q6r7s8"},
                    ]
                },
            },
            "without_dealer": {
                "summary": "Bayi olmadan (alanı hiç gönderme)",
                "value": {
                    "vehicleType": 1,
                    "vehicleCapacity": 80,
                    "stateId": 6,
                    "vehicleYear": 2018,
                    "documents": [
                        {"docType": "VergiLevhasi", "fileId": "c9c9e6f4-9db9-4b1a-8f90-7c0f1fb2a4cd"},
                        {"docType": "EhliyetOn",  "fileId": "5b2b1f16-6e87-4f2b-9d9e-1e0b0d0a1f22"},
                        {"docType": "EhliyetArka","fileId": "3a1a2b3c-4d5e-6f70-8g90-1h2i3j4k5l6m"},
                        {"docType": "RuhsatOn",  "fileId": "7n8o9p0q-1r2s-3t4u-5v6w-7x8y9z0a1b2c"},
                        {"docType": "RuhsatArka",  "fileId": "7n8o9p0q-1r2s-3t4u-5v6w-7x8y9z0a1b2c"},
                        {"docType": "KimlikOn","fileId": "d3e4f5g6-h7i8-j9k0-l1m2-n3o4p5q6r7s8"},
                        {"docType": "KimlikArka","fileId": "d3e4f5g6-h7i8-j9k0-l1m2-n3o4p5q6r7s8"},
                    ]
                },
            },
            "dealer_null": {
                "summary": "Bayi null (opsiyonel/nullable alan)",
                "value": {
                    "vehicleType": 2,
                    "vehicleCapacity": 120,
                    "stateId": 35,
                    "vehicleYear": 2022,
                    "dealer_id": None,
                    "documents": [
                        {"docType": "VergiLevhasi", "fileId": "c9c9e6f4-9db9-4b1a-8f90-7c0f1fb2a4cd"},
                        {"docType": "EhliyetOn",  "fileId": "5b2b1f16-6e87-4f2b-9d9e-1e0b0d0a1f22"},
                        {"docType": "EhliyetArka","fileId": "3a1a2b3c-4d5e-6f70-8g90-1h2i3j4k5l6m"},
                        {"docType": "RuhsatOn",  "fileId": "7n8o9p0q-1r2s-3t4u-5v6w-7x8y9z0a1b2c"},
                        {"docType": "RuhsatArka",  "fileId": "7n8o9p0q-1r2s-3t4u-5v6w-7x8y9z0a1b2c"},
                        {"docType": "KimlikOn","fileId": "d3e4f5g6-h7i8-j9k0-l1m2-n3o4p5q6r7s8"},
                        {"docType": "KimlikArka","fileId": "d3e4f5g6-h7i8-j9k0-l1m2-n3o4p5q6r7s8"},
                    ]
                },
            },
        },
    ),
):
    return await ctrl.courier_register3(user_id, req)


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
                                    "vehicleYear": 2020,
                                    "is_active": True,
                                    "deleted" : False,
                                    "deleted_at": None
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
async def get_courier_profile(
    user_id: str = Path(..., description="The UUID of the courier user"),
    _claims = Depends(auth_controller.require_roles(["Courier","Admin"]))
):
    return await ctrl.get_courier_profile(user_id)


@router.get(
    "/list",
    summary="Get Courier List",
    description="Fetches the profile information of all couriers (visible to Admin, Courier, and Restaurant roles).",
    responses={
        200: {
            "description": "Courier list retrieved successfully.",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Successful response",
                            "value": {
                                "success": True,
                                "message": "Courier list",
                                "data": [
                                    {
                                        "userId": "6aef8f5c-27e0-4e8c-8b2d-36a78b6a0b0a",
                                        "phone": "5551112233",
                                        "firstName": "Test",
                                        "lastName": "Test",
                                        "email": "test@test.com",
                                        "createdAt": "2023-10-01T12:34:56Z",
                                        "countryId": 90,
                                        "dealer_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                                        "is_online": True,
                                        "countryName": "Turkey",
                                        "stateId": 34,
                                        "stateName": "Istanbul",
                                        "workingType": 1,
                                        "vehicleType": 0,
                                        "vehicleCapacity": 100,
                                        "vehicleYear": 2020,
                                        "is_active": True,
                                        "deleted": False,
                                        "deleted_at": None
                                    }
                                ]
                            }
                        },
                        "not_found": {
                            "summary": "No couriers found",
                            "value": {
                                "success": False,
                                "message": "No couriers found",
                                "data": {}
                            }
                        }
                    }
                }
            },
        }
    },
)

async def list_couriers( _claims = Depends(auth_controller.require_roles(["Courier","Admin","Restaurant", "Dealer"]))):
    return await ctrl.list_couriers(_claims)

@router.get(
    "/{user_id}/get_documents",
    summary="Get Courier Documents",
    description="Fetches the documents of a courier by user ID.",
    responses={
        200: {
            "description": "Courier documents retrieved successfully.",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Successful response",
                            "value": {
                                "success": True,
                                "message": "Courier documents",
                                "data": [
                                        {
                                        "document_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                                        "doc_type": "KimlikArka",
                                        "file_id": "4185b628-312f-4c40-bb84-1f75ee0749fc",
                                        "document_status": "inceleme_bekleniyor",
                                        "image_url": "https://cdn.filestackcontent.com/HLURGSHTa21ujC2o8prf",
                                        "uploaded_at": "2025-10-13T13:44:08.451586+03:00"
                                        },
                                        {
                                            "document_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                                        "doc_type": "KimlikOn",
                                        "file_id": "4185b628-312f-4c40-bb84-1f75ee0749fc",
                                        "document_status": "inceleme_bekleniyor",
                                        "image_url": "https://cdn.filestackcontent.com/HLURGSHTa21ujC2o8prf",
                                        "uploaded_at": "2025-10-13T13:44:08.451586+03:00"
                                        },
                                        {
                                            "document_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                                        "doc_type": "RuhsatArka",
                                        "file_id": "4185b628-312f-4c40-bb84-1f75ee0749fc",
                                        "document_status": "inceleme_bekleniyor",
                                        "image_url": "https://cdn.filestackcontent.com/HLURGSHTa21ujC2o8prf",
                                        "uploaded_at": "2025-10-13T13:44:08.451586+03:00"
                                        },
                                        {
                                            "document_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                                        "doc_type": "RuhsatOn",
                                        "file_id": "4185b628-312f-4c40-bb84-1f75ee0749fc",
                                        "document_status": "inceleme_bekleniyor",
                                        "image_url": "https://cdn.filestackcontent.com/HLURGSHTa21ujC2o8prf",
                                        "uploaded_at": "2025-10-13T13:44:08.451586+03:00"
                                        },
                                        {
                                            "document_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                                        "doc_type": "EhliyetArka",
                                        "file_id": "4185b628-312f-4c40-bb84-1f75ee0749fc",
                                        "document_status": "inceleme_bekleniyor",
                                        "image_url": "https://cdn.filestackcontent.com/HLURGSHTa21ujC2o8prf",
                                        "uploaded_at": "2025-10-13T13:44:08.451586+03:00"
                                        },
                                        {
                                        "doc_type": "EhliyetOn",
                                        "file_id": "4185b628-312f-4c40-bb84-1f75ee0749fc",
                                        "document_status": "inceleme_bekleniyor",
                                        "image_url": "https://cdn.filestackcontent.com/HLURGSHTa21ujC2o8prf",
                                        "uploaded_at": "2025-10-13T13:44:08.451586+03:00"
                                        },
                                        {
                                            "document_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                                        "doc_type": "VergiLevhasi",
                                        "file_id": "4185b628-312f-4c40-bb84-1f75ee0749fc",
                                        "document_status": "inceleme_bekleniyor",
                                        "image_url": "https://cdn.filestackcontent.com/HLURGSHTa21ujC2o8prf",
                                        "uploaded_at": "2025-10-13T13:44:08.451586+03:00"
                                        }
                                ]
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
async def get_courier_documents(
    user_id: UUID = Path(..., description="The UUID of the courier user"),
    _claims = Depends(auth_controller.require_roles(["Courier","Admin","Restaurant", "Dealer"]))
):
    return await ctrl.get_courier_documents(user_id, _claims)


@router.put(
    "/{user_id}/update_documents_status/{document_id}",
    summary="Update Courier Document Status",
    description="Updates the status of a specific courier document. Types of status include: 'evrak_bekleniyor', 'inceleme_bekleniyor', 'eksik_belge', 'reddedildi', 'onaylandi'.",
    responses={
        200: {
            "description": "Courier document status updated successfully.",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Successful response",
                            "value": {
                                "success": True,
                                "message": "Courier document status updated",
                                "data": {}
                            }
                        },
                        "not_found": {
                            "summary": "Courier document not found",
                            "value": {
                                "success": False,
                                "message": "Courier document not found",
                                "data": {}
                            }
                        }
                    }
                }
            },
        }
    },
)
async def update_courier_document_status(
    user_id: UUID = Path(..., description="The UUID of the courier user"),
    document_id: UUID = Path(..., description="The UUID of the document to update"),
    new_status: str = Body(..., embed=True, description="The new status for the document"),
    _claims = Depends(auth_controller.require_roles(["Admin", "Dealer"]))
):
    return await ctrl.update_courier_document_status(user_id, document_id, new_status, _claims)
    

@router.delete(
    "/{user_id}/delete",
    summary="Delete Courier User",
    description="Soft deletes a courier user by setting the 'deleted' flag and 'deleted_at' timestamp.",
    responses={
        200: {
            "description": "Courier user deleted successfully.",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Successful response",
                            "value": {
                                "success": True,
                                "message": "Courier user deleted successfully",
                                "data": {}
                            }
                        },
                        "not_found": {
                            "summary": "Courier user not found",
                            "value": {
                                "success": False,
                                "message": "Courier user not found",
                                "data": {}
                            }
                        }
                    }
                }
            },
        }
    },
)
async def delete_courier_user(
    user_id: UUID = Path(..., description="The UUID of the courier user to delete"),
    _claims = Depends(auth_controller.require_roles(["Admin"]))
):
    return await ctrl.delete_courier_user(user_id)

@router.put(
    "/{user_id}/profile/update",
    summary="Update Courier Profile",
    description="Updates the profile information of a courier by user ID.",
    responses={
        200: {
            "description": "Courier profile updated successfully.",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Successful response",
                            "value": {
                                "success": True,
                                "message": "Courier profile updated successfully",
                                "data": {}
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
async def update_courier_profile(
    user_id: str = Path(..., description="The UUID of the courier user"),
    req: CourierProfileUpdateReq = Body(...),
    _claims = Depends(auth_controller.require_roles(["Courier","Admin"]))
):
    return await ctrl.update_courier_profile(user_id, req)


@router.get(
    "/{state_id}/get_dealers",
    summary="Get Dealers by State",
    description="Fetches a list of dealers operating in the specified state.",
    responses={
        200: {
            "description": "Dealers retrieved successfully.",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Successful response",
                            "value": {
                                "success": True,
                                "message": "Dealers list",
                                "data": [
                                    {
                                        "dealer_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                                        "dealer_name": "Yuksi Dealer 1",
                                        "state_id": 34,
                                        "state_name": "Istanbul",
                                        "address": "123 Yuksi St, Istanbul",
                                        "phone": "5551234567",
                                        "email": "dealer@yuksi.com"
                                    }
                                ]
                            }
                        },
                        "not_found": {
                            "summary": "No dealers found",
                            "value": {
                                "success": False,
                                "message": "No dealers found in the specified city",
                                "data": {}
                            }
                        }
                    }
                }
            },
        }
    },
)
async def get_dealers_by_state(
    state_id: int = Path(..., description="The ID of the state to fetch dealers for")
):
    return await ctrl.get_dealers_by_state(state_id)


# ===== DASHBOARD ENDPOINTS (Ayrı endpoint'ler) =====

@router.get(
    "/{courier_id}/dashboard/earnings",
    summary="Kurye Kazanç Verileri",
    description="Kurye kazanç verilerini getirir (toplam ve günlük kazanç)",
    responses={
        200: {
            "description": "Kazanç verileri başarıyla getirildi.",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Başarılı yanıt",
                            "value": {
                                "success": True,
                                "message": "Kurye kazanç verileri",
                                "data": {
                                    "total_earnings": 19502.50,
                                    "daily_earnings": 920.00
                                }
                            }
                        }
                    }
                }
            },
        }
    },
)
async def get_courier_earnings(
    courier_id: str = Path(..., description="Kurye UUID'si"),
    _claims = Depends(auth_controller.require_roles(["Courier", "Admin"]))
):
    from ..controllers import courier_dashboard_controller as dashboard_ctrl
    return await dashboard_ctrl.get_courier_earnings(courier_id)


@router.get(
    "/{courier_id}/dashboard/distance",
    summary="Kurye Mesafe Verileri",
    description="Kurye mesafe verilerini getirir (toplam ve günlük km)",
    responses={
        200: {
            "description": "Mesafe verileri başarıyla getirildi.",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Başarılı yanıt",
                            "value": {
                                "success": True,
                                "message": "Kurye mesafe verileri",
                                "data": {
                                    "total_km": 348.2,
                                    "daily_km": 28.5
                                }
                            }
                        }
                    }
                }
            },
        }
    },
)
async def get_courier_distance(
    courier_id: str = Path(..., description="Kurye UUID'si"),
    _claims = Depends(auth_controller.require_roles(["Courier", "Admin"]))
):
    from ..controllers import courier_dashboard_controller as dashboard_ctrl
    return await dashboard_ctrl.get_courier_distance(courier_id)


@router.get(
    "/{courier_id}/dashboard/package",
    summary="Kurye Paket Bilgileri",
    description="Kurye paket bilgilerini getirir (kalan gün ve faaliyet süresi)",
    responses={
        200: {
            "description": "Paket bilgileri başarıyla getirildi.",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Başarılı yanıt",
                            "value": {
                                "success": True,
                                "message": "Kurye paket bilgileri",
                                "data": {
                                    "remaining_days": 17,
                                    "total_activity_duration_days": 22,
                                    "total_activity_duration_hours": 16
                                }
                            }
                        }
                    }
                }
            },
        }
    },
)
async def get_courier_package(
    courier_id: str = Path(..., description="Kurye UUID'si"),
    _claims = Depends(auth_controller.require_roles(["Courier", "Admin"]))
):
    from ..controllers import courier_dashboard_controller as dashboard_ctrl
    return await dashboard_ctrl.get_courier_package(courier_id)


@router.get(
    "/{courier_id}/dashboard/work-hours",
    summary="Kurye Çalışma Saatleri",
    description="Kurye çalışma saatlerini getirir (günlük ve toplam). Paket bitmişse her ikisi de 0 döner.",
    responses={
        200: {
            "description": "Çalışma saatleri başarıyla getirildi.",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Başarılı yanıt",
                            "value": {
                                "success": True,
                                "message": "Kurye çalışma saatleri",
                                "data": {
                                    "daily_work_time": "5:30",
                                    "total_work_time": "45:15"
                                }
                            }
                        }
                    }
                }
            },
        }
    },
)
async def get_courier_work_hours(
    courier_id: str = Path(..., description="Kurye UUID'si"),
    _claims = Depends(auth_controller.require_roles(["Courier", "Admin"]))
):
    from ..controllers import courier_dashboard_controller as dashboard_ctrl
    return await dashboard_ctrl.get_courier_work_hours(courier_id)


@router.get(
    "/{courier_id}/dashboard/activities",
    summary="Kurye Aktivite Sayısı",
    description="Kurye toplam aktivite sayısını getirir",
    responses={
        200: {
            "description": "Aktivite sayısı başarıyla getirildi.",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Başarılı yanıt",
                            "value": {
                                "success": True,
                                "message": "Kurye aktivite sayısı",
                                "data": {
                                    "total_activities": 16
                                }
                            }
                        }
                    }
                }
            },
        }
    },
)
async def get_courier_activities(
    courier_id: str = Path(..., description="Kurye UUID'si"),
    _claims = Depends(auth_controller.require_roles(["Courier", "Admin"]))
):
    from ..controllers import courier_dashboard_controller as dashboard_ctrl
    return await dashboard_ctrl.get_courier_activities(courier_id)


# ===== DEPRECATED: Combined Dashboard Endpoint =====
@router.get(
    "/{courier_id}/dashboard",
    summary="Kurye Dashboard (KULLANIMDIŞI)",
    description="Kurye dashboard verilerini getirir (KULLANIMDIŞI - ayrı endpoint'ler kullanılmalı: /earnings, /distance, /package, /work-hours, /activities)",
    deprecated=True,
    responses={
        200: {
            "description": "Dashboard verileri başarıyla getirildi.",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Başarılı yanıt",
                            "value": {
                                "success": True,
                                "message": "Kurye dashboard verileri",
                                "data": {
                                    "total_earnings": 19502.50,
                                    "daily_earnings": 920.00,
                                    "total_activity_duration_days": 22,
                                    "total_activity_duration_hours": 16,
                                    "remaining_days": 17,
                                    "daily_km": 28.5,
                                    "total_km": 348.2,
                                    "total_activities": 16,
                                    "daily_work_time": "5:30",
                                    "total_work_time": "45:15"
                                }
                            }
                        }
                    }
                }
            },
        }
    },
)
async def get_courier_dashboard(
    courier_id: str = Path(..., description="Kurye UUID'si"),
    _claims = Depends(auth_controller.require_roles(["Courier", "Admin"]))
):
    from ..controllers import courier_dashboard_controller as dashboard_ctrl
    return await dashboard_ctrl.get_courier_dashboard(courier_id)


@router.get(
    "/history",
    response_model=CourierHistoryRes,
    summary="Kurye Aktivite Geçmişi",
    description="Kurye aktivite geçmişini tarih filtresi ve sayfalama ile getirir.",
)
async def get_courier_history(
    date : str = Query(None, description="Tarih filtresi (YYYY-MM-DD formatında)"),
    page : int = Query(1, ge=1, description="Sayfa numarası"),
    page_size : int = Query(25, ge=1, le=100, description="Sayfa başına kayıt sayısı"),
    _claims = Depends(auth_controller.require_roles(["Courier"]))
):
    return await ctrl.get_courier_history(_claims, date, page, page_size)

@router.put(
    "/{order_id}/update-status",
    response_model=CourierOrderStatusChangeRes,
    summary="Kurye Sipariş Durumu Değişikliği",
    description="Kuryenin sipariş durumu değiştirmesini sağlar.",
)
async def change_courier_order_status(
    order_id: str = Path(..., description="Sipariş UUID'si"),
    req: CourierOrderStatusChangeReq = Body(...),
    _claims = Depends(auth_controller.require_roles(["Courier"]))
):
    return await ctrl.change_courier_order_status(_claims, order_id, req)