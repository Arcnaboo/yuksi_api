from fastapi import APIRouter, Path, Body, Depends
from ..models.courier_model import (
    CourierRegisterStep1Req,
    CourierRegisterStep2Req,
    CourierRegisterStep3Req,
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
    req: CourierRegisterStep3Req = Body(...),
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

async def list_couriers( _claims = Depends(auth_controller.require_roles(["Courier","Admin","Restaurant"]))):
    return await ctrl.list_couriers()

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
    _claims = Depends(auth_controller.require_roles(["Courier","Admin","Restaurant"]))
):
    return await ctrl.get_courier_documents(user_id)


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
    _claims = Depends(auth_controller.require_roles(["Admin"]))
):
    return await ctrl.update_courier_document_status(user_id, document_id, new_status)
    

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