import json
import re
from openai import OpenAI
from app.utils.config import get_openai_api_key

# OpenAI client başlatma
client = OpenAI(api_key=get_openai_api_key())

# AI prompt
PROMPT = """Given the image of a cargo/load, determine the required vehicle type.

You must choose ONE of the following vehicle types:
- MOTOKURYE (Motorcycle Courier - for small, light packages)
- PANELVAN (Panel Van - for medium-sized cargo)
- MINIVAN (Minivan - for larger items)
- FULL_VAN (Full Van - for very large cargo)
- KAMYONET (Pickup Truck - for heavy or bulky items)

Analyze the image and return a JSON response with:
- "vehicle": one of the vehicle types above
- "confidence": integer from 0-100 representing your confidence level
- "reason": brief explanation of why this vehicle type was chosen

Return ONLY valid JSON, no other text."""

# Araç tipi mapping (AI'dan gelen → Sistem değeri)
VEHICLE_MAPPING = {
    "MOTOKURYE": "motorcycle",
    "PANELVAN": "panelvan",
    "MINIVAN": "minivan",
    "FULL_VAN": "kamyon",
    "KAMYONET": "kamyonet"
}


async def analyze_cargo(image_url: str) -> dict:
    """
    Yük fotoğrafını analiz eder ve uygun araç tipini belirler.
    
    Args:
        image_url: Filestack'ten gelen görsel URL'i
        
    Returns:
        dict: {
            "vehicle": "kamyon",  # mapped sistem değeri
            "confidence": 92,
            "reason": "Large household appliance detected",
            "original_vehicle": "FULL_VAN"  # AI'dan gelen orijinal değer
        }
        
    Raises:
        RuntimeError: OpenAI API hatası veya JSON parse hatası
    """
    try:
        # GPT-4o ile görsel analiz
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        }
                    ]
                }
            ],
            max_tokens=300,
            temperature=0.3
        )
        
        # Response'dan text al
        response_text = response.choices[0].message.content.strip()
        
        # JSON parse et
        try:
            # Eğer response text JSON içinde değilse, sadece JSON kısmını al
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            analysis = json.loads(response_text)
        except json.JSONDecodeError:
            # JSON parse edilemezse, default değer döndür
            raise RuntimeError(f"AI yanıtı JSON formatında parse edilemedi: {response_text}")
        
        # Gerekli alanları kontrol et
        original_vehicle = analysis.get("vehicle", "").upper()
        if not original_vehicle or original_vehicle not in VEHICLE_MAPPING:
            # Geçersiz araç tipi gelirse, default olarak MINIVAN döndür
            original_vehicle = "MINIVAN"
            analysis["vehicle"] = original_vehicle
            analysis["confidence"] = analysis.get("confidence", 50)
            analysis["reason"] = "Araç tipi belirlenemedi, varsayılan olarak MINIVAN kullanılıyor"
        
        # Sistem değerine map et
        mapped_vehicle = VEHICLE_MAPPING.get(original_vehicle, "minivan")
        
        return {
            "vehicle": mapped_vehicle,
            "confidence": analysis.get("confidence", 0),
            "reason": analysis.get("reason", "Araç tipi AI analizi ile belirlendi"),
            "original_vehicle": original_vehicle
        }
        
    except Exception as e:
        error_str = str(e)
        # OpenAI hatasını parse et ve daha okunabilir hale getir
        try:
            # 401 Unauthorized - API key hatası
            if "401" in error_str or "Error code: 401" in error_str:
                if "Incorrect API key" in error_str or "invalid_api_key" in error_str:
                    raise RuntimeError("OpenAI API anahtarı geçersiz veya yanlış. Lütfen .env dosyasındaki OPENAI_API_KEY değerini kontrol edin. API anahtarınızı https://platform.openai.com/account/api-keys adresinden alabilirsiniz.")
                else:
                    raise RuntimeError("OpenAI API yetkilendirme hatası. API anahtarınızı kontrol edin.")
            
            # 429 Rate Limit
            elif "429" in error_str or "Error code: 429" in error_str or "rate_limit" in error_str.lower():
                raise RuntimeError("OpenAI API limiti aşıldı. Lütfen daha sonra tekrar deneyin.")
            
            # 500 Server Error
            elif "500" in error_str or "Error code: 500" in error_str:
                raise RuntimeError("OpenAI API sunucu hatası. Lütfen daha sonra tekrar deneyin.")
            
            # Hata mesajı içinde 'message' varsa çıkar
            elif "'message':" in error_str or '"message":' in error_str:
                # Message'ı bul
                message_match = re.search(r"['\"]message['\"]:\s*['\"]([^'\"]+)['\"]", error_str)
                if message_match:
                    error_message = message_match.group(1)
                    raise RuntimeError(f"OpenAI API hatası: {error_message}")
            
            # Diğer hatalar
            raise RuntimeError(f"OpenAI API hatası: {error_str}")
            
        except RuntimeError:
            # Zaten RuntimeError ise tekrar fırlat
            raise
        except Exception:
            # Parse edilemezse orijinal hatayı kullan
            raise RuntimeError(f"OpenAI API hatası: {error_str}")
