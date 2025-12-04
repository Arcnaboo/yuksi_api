from fastapi import APIRouter, Query, Depends, Path
from typing import Optional
from uuid import UUID
from app.controllers import support_courier_controller
from app.controllers.auth_controller import require_support_module

router = APIRouter(prefix="/api/support", tags=["Support Modules"])

# ============================================
# MODÜL 1: KURYELER
# ============================================

@router.get(
    "/couriers",
    summary="Kurye Listesi (Çağrı Merkezi - Modül 1)",
    description="Çağrı merkezi için tüm kuryelerin listesini getirir. Modül 1 yetkisi gereklidir.",
    dependencies=[Depends(require_support_module(1))],
)
async def get_support_couriers(
    limit: int = Query(50, ge=1, le=200, description="Maksimum kayıt sayısı"),
    offset: int = Query(0, ge=0, description="Sayfalama offset"),
    search: Optional[str] = Query(None, description="Arama terimi (ad, soyad, email, telefon)"),
    claims: dict = Depends(require_support_module(1))
):
    """
    Çağrı merkezi için kurye listesi endpoint'i.
    Sadece Modül 1 (Kuryeler) yetkisine sahip support kullanıcıları erişebilir.
    
    **Dönen Bilgiler:**
    - Kurye temel bilgileri (ad, soyad, email, telefon)
    - Onboarding bilgileri (ülke, şehir, araç tipi, vs.)
    - Online durumu
    - Konum bilgisi (varsa)
    """
    return await support_courier_controller.get_support_couriers(
        limit=limit,
        offset=offset,
        search=search
    )


@router.get(
    "/couriers/{courier_id}",
    summary="Kurye Detayı (Çağrı Merkezi - Modül 1)",
    description="Çağrı merkezi için belirli bir kuryenin detaylarını getirir. Modül 1 yetkisi gereklidir.",
    dependencies=[Depends(require_support_module(1))],
)
async def get_support_courier_detail(
    courier_id: UUID = Path(..., description="Kurye ID'si"),
    claims: dict = Depends(require_support_module(1))
):
    """
    Çağrı merkezi için kurye detayı endpoint'i.
    Sadece Modül 1 (Kuryeler) yetkisine sahip support kullanıcıları erişebilir.
    
    **Dönen Bilgiler:**
    - Kurye tüm detayları
    - Onboarding bilgileri
    - Online durumu
    - Konum bilgisi
    """
    return await support_courier_controller.get_support_courier_detail(str(courier_id))


@router.get(
    "/couriers/{courier_id}/packages",
    summary="Kurye Paketleri (Çağrı Merkezi - Modül 1)",
    description="Çağrı merkezi için kuryenin taşıdığı paketleri (siparişleri) getirir. Modül 1 yetkisi gereklidir.",
    dependencies=[Depends(require_support_module(1))],
)
async def get_support_courier_packages(
    courier_id: UUID = Path(..., description="Kurye ID'si"),
    limit: int = Query(50, ge=1, le=200, description="Maksimum kayıt sayısı"),
    offset: int = Query(0, ge=0, description="Sayfalama offset"),
    status: Optional[str] = Query(None, description="Sipariş durumu filtresi"),
    claims: dict = Depends(require_support_module(1))
):
    """
    Çağrı merkezi için kurye paketleri endpoint'i.
    Sadece Modül 1 (Kuryeler) yetkisine sahip support kullanıcıları erişebilir.
    
    **Dönen Bilgiler:**
    - Kuryenin taşıdığı tüm siparişler
    - Sipariş detayları (müşteri, adres, durum, vs.)
    - Restoran bilgileri
    """
    return await support_courier_controller.get_support_courier_packages(
        courier_id=str(courier_id),
        limit=limit,
        offset=offset,
        status=status
    )


@router.get(
    "/couriers/{courier_id}/location",
    summary="Kurye Konumu (Çağrı Merkezi - Modül 1)",
    description="Çağrı merkezi için kuryenin anlık konumunu getirir. Modül 1 yetkisi gereklidir.",
    dependencies=[Depends(require_support_module(1))],
)
async def get_support_courier_location(
    courier_id: UUID = Path(..., description="Kurye ID'si"),
    claims: dict = Depends(require_support_module(1))
):
    """
    Çağrı merkezi için kurye konumu endpoint'i.
    Sadece Modül 1 (Kuryeler) yetkisine sahip support kullanıcıları erişebilir.
    
    **Dönen Bilgiler:**
    - Kuryenin GPS koordinatları (latitude, longitude)
    - Konum güncelleme zamanı
    - Online durumu
    """
    return await support_courier_controller.get_support_courier_location(str(courier_id))


@router.get(
    "/couriers/{courier_id}/stats",
    summary="Kurye İstatistikleri (Çağrı Merkezi - Modül 1)",
    description="Çağrı merkezi için kurye istatistiklerini getirir (kaç paket attı, mesafe, paket bilgileri, mola durumu). Modül 1 yetkisi gereklidir.",
    dependencies=[Depends(require_support_module(1))],
)
async def get_support_courier_stats(
    courier_id: UUID = Path(..., description="Kurye ID'si"),
    claims: dict = Depends(require_support_module(1))
):
    """
    Çağrı merkezi için kurye istatistikleri endpoint'i.
    Sadece Modül 1 (Kuryeler) yetkisine sahip support kullanıcıları erişebilir.
    
    **Dönen Bilgiler:**
    - Teslim edilen paket sayısı
    - Toplam mesafe (km)
    - Günlük mesafe (km)
    - Paket bilgileri (subscription)
    - Mola durumu
    """
    return await support_courier_controller.get_support_courier_stats(str(courier_id))

