from typing import Dict, Any
from fastapi import UploadFile
from app.services import user_job_service as svc


async def user_create_job(data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    success, result = await svc.user_create_job(data, user_id)
    if not success:
        return {"success": False, "message": result, "data": {}}
    return {"success": True, "message": "Yük başarıyla oluşturuldu.", "data": {"jobId": result}}


async def user_get_jobs(
    user_id: str,
    limit: int, 
    offset: int, 
    delivery_type: str | None
) -> Dict[str, Any]:
    success, result = await svc.user_get_jobs(user_id, limit, offset, delivery_type)
    if not success:
        return {"success": False, "message": result, "data": []}
    return {"success": True, "message": "Yük listesi getirildi.", "data": result}


async def user_get_job(job_id: str, user_id: str) -> Dict[str, Any]:
    success, result = await svc.user_get_job(job_id, user_id)
    if not success:
        return {"success": False, "message": result, "data": {}}
    return {"success": True, "message": "Yük detayı getirildi.", "data": result}


async def user_update_job(
    job_id: str, 
    user_id: str,
    fields: Dict[str, Any]
) -> Dict[str, Any]:
    success, error = await svc.user_update_job(job_id, user_id, fields)
    if not success:
        return {"success": False, "message": error, "data": {}}
    return {"success": True, "message": "Yük başarıyla güncellendi.", "data": {}}


async def user_delete_job(job_id: str, user_id: str) -> Dict[str, Any]:
    success, error = await svc.user_delete_job(job_id, user_id)
    if not success:
        return {"success": False, "message": error, "data": {}}
    return {"success": True, "message": "Yük başarıyla silindi.", "data": {}}


async def user_cargo_scan(file: UploadFile) -> Dict[str, Any]:
    """
    Yük fotoğrafını analiz eder ve uygun araç tipini önerir.
    Fotoğraf sisteme kaydedilmez, sadece analiz için kullanılır.
    """
    if not file:
        return {"success": False, "message": "Dosya gerekli.", "data": {}}
    
    # Dosyayı oku
    try:
        file_data = await file.read()
        if not file_data:
            return {"success": False, "message": "Boş dosya.", "data": {}}
    except Exception as e:
        return {"success": False, "message": f"Dosya okunamadı: {str(e)}", "data": {}}
    
    # Service'i çağır
    success, result = await svc.user_cargo_scan_temporary(
        file_data=file_data,
        filename=file.filename or "cargo.jpg",
        mimetype=file.content_type or "image/jpeg"
    )
    
    if not success:
        return {"success": False, "message": result, "data": {}}
    
    return {
        "success": True,
        "message": "Yük analizi tamamlandı.",
        "data": result
    }

