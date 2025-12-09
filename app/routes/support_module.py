from fastapi import APIRouter, Query, Depends, Path, Body, HTTPException
from typing import Optional
from uuid import UUID
from app.controllers import support_courier_controller, support_restaurant_controller
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


# ============================================
# MODÜL 3: RESTORANLAR
# ============================================

@router.get(
    "/restaurants",
    summary="Restoran Listesi (Çağrı Merkezi - Modül 3)",
    description="Çağrı merkezi için tüm restoranların listesini getirir. Hangi bayinin eklediği bilgisi dahil. Modül 3 yetkisi gereklidir.",
    dependencies=[Depends(require_support_module(3))],
)
async def get_support_restaurants(
    limit: int = Query(50, ge=1, le=200, description="Maksimum kayıt sayısı"),
    offset: int = Query(0, ge=0, description="Sayfalama offset"),
    search: Optional[str] = Query(None, description="Arama terimi (ad, email, telefon, vergi no)"),
    claims: dict = Depends(require_support_module(3))
):
    """
    Çağrı merkezi için restoran listesi endpoint'i.
    Sadece Modül 3 (Restoranlar) yetkisine sahip support kullanıcıları erişebilir.
    
    **Dönen Bilgiler:**
    - Restoran temel bilgileri (ad, email, telefon, vergi no)
    - Adres bilgileri (şehir, il, ülke)
    - Konum bilgisi (latitude, longitude)
    - Hangi bayinin eklediği bilgisi
    - Açılış/kapanış saatleri
    """
    return await support_restaurant_controller.get_support_restaurants(
        limit=limit,
        offset=offset,
        search=search
    )


@router.get(
    "/restaurants/{restaurant_id}",
    summary="Restoran Detayı (Çağrı Merkezi - Modül 3)",
    description="Çağrı merkezi için belirli bir restoranın detaylarını getirir. Tüm bilgiler, günlük paket durumu, konum, vs. Modül 3 yetkisi gereklidir.",
    dependencies=[Depends(require_support_module(3))],
)
async def get_support_restaurant_detail(
    restaurant_id: UUID = Path(..., description="Restoran ID'si"),
    claims: dict = Depends(require_support_module(3))
):
    """
    Çağrı merkezi için restoran detayı endpoint'i.
    Sadece Modül 3 (Restoranlar) yetkisine sahip support kullanıcıları erişebilir.
    
    **Dönen Bilgiler:**
    - Restoran tüm detayları
    - Hangi bayinin eklediği bilgisi
    - Konum bilgisi
    - Günlük paket durumu
    - Kurye sayısı
    """
    return await support_restaurant_controller.get_support_restaurant_detail(str(restaurant_id))


@router.put(
    "/restaurants/{restaurant_id}",
    summary="Restoran Güncelle (Çağrı Merkezi - Modül 3)",
    description="Çağrı merkezi için restoran bilgilerini günceller (sistemsel müdahale için). Tüm alanlar opsiyoneldir. Modül 3 yetkisi gereklidir.",
    dependencies=[Depends(require_support_module(3))],
)
async def update_support_restaurant(
    restaurant_id: UUID = Path(..., description="Restoran ID'si"),
    email: Optional[str] = Body(None, description="E-posta adresi"),
    phone: Optional[str] = Body(None, description="Telefon numarası"),
    name: Optional[str] = Body(None, description="Restoran adı"),
    contact_person: Optional[str] = Body(None, description="İletişim kişisi"),
    tax_number: Optional[str] = Body(None, description="Vergi numarası"),
    address_line1: Optional[str] = Body(None, description="Adres satırı 1"),
    address_line2: Optional[str] = Body(None, description="Adres satırı 2"),
    opening_hour: Optional[str] = Body(None, description="Açılış saati (HH:MM formatında)"),
    closing_hour: Optional[str] = Body(None, description="Kapanış saati (HH:MM formatında)"),
    latitude: Optional[float] = Body(None, description="Enlem"),
    longitude: Optional[float] = Body(None, description="Boylam"),
    claims: dict = Depends(require_support_module(3))
):
    """
    Çağrı merkezi için restoran güncelleme endpoint'i.
    Sadece Modül 3 (Restoranlar) yetkisine sahip support kullanıcıları erişebilir.
    
    **Güncellenebilir Alanlar:**
    - email: E-posta adresi
    - phone: Telefon numarası
    - name: Restoran adı
    - contact_person: İletişim kişisi
    - tax_number: Vergi numarası
    - address_line1: Adres satırı 1
    - address_line2: Adres satırı 2
    - opening_hour: Açılış saati (HH:MM)
    - closing_hour: Kapanış saati (HH:MM)
    - latitude: Enlem
    - longitude: Boylam
    
    **Not:** Tüm alanlar opsiyoneldir. Sadece gönderilen alanlar güncellenir.
    """
    return await support_restaurant_controller.update_support_restaurant(
        restaurant_id=str(restaurant_id),
        email=email,
        phone=phone,
        name=name,
        contact_person=contact_person,
        tax_number=tax_number,
        address_line1=address_line1,
        address_line2=address_line2,
        opening_hour=opening_hour,
        closing_hour=closing_hour,
        latitude=latitude,
        longitude=longitude,
    )


@router.get(
    "/restaurants/{restaurant_id}/package",
    summary="Restoran Paket Durumu (Çağrı Merkezi - Modül 3)",
    description="Çağrı merkezi için restoranın günlük paket durumunu getirir. Modül 3 yetkisi gereklidir.",
    dependencies=[Depends(require_support_module(3))],
)
async def get_support_restaurant_package(
    restaurant_id: UUID = Path(..., description="Restoran ID'si"),
    claims: dict = Depends(require_support_module(3))
):
    """
    Çağrı merkezi için restoran paket durumu endpoint'i.
    Sadece Modül 3 (Restoranlar) yetkisine sahip support kullanıcıları erişebilir.
    
    **Dönen Bilgiler:**
    - Maksimum paket sayısı
    - Teslim edilen paket sayısı
    - Kalan paket sayısı
    - Toplam paket sipariş sayısı
    - Uyarı mesajları (varsa)
    """
    return await support_restaurant_controller.get_support_restaurant_package(str(restaurant_id))

