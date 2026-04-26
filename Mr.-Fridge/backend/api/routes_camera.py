from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.vision_service import identify_item_from_base64

router = APIRouter(prefix="/camera", tags=["Camera"])

# Kategori tahmini — basit kural tabanlı (LLM'e kadar geçici)
CATEGORY_MAP = {
    "süt": "Süt Ürünleri", "yoğurt": "Süt Ürünleri", "peynir": "Süt Ürünleri",
    "tereyağ": "Süt Ürünleri", "krema": "Süt Ürünleri",
    "elma": "Meyve", "muz": "Meyve", "portakal": "Meyve", "çilek": "Meyve",
    "üzüm": "Meyve", "kivi": "Meyve", "armut": "Meyve",
    "domates": "Sebze", "salatalık": "Sebze", "biber": "Sebze", "brokoli": "Sebze",
    "havuç": "Sebze", "soğan": "Sebze", "sarımsak": "Sebze", "ispanak": "Sebze",
    "tavuk": "Et & Balık", "kıyma": "Et & Balık", "balık": "Et & Balık",
    "sosis": "Et & Balık", "sucuk": "Et & Balık",
    "yumurta": "Temel Gıda", "ekmek": "Temel Gıda", "makarna": "Temel Gıda",
    "pirinç": "Temel Gıda", "un": "Temel Gıda",
    "meyve suyu": "İçecek", "kola": "İçecek", "su": "İçecek",
}


def guess_category(item_name: str) -> str:
    lower = item_name.lower()
    for keyword, category in CATEGORY_MAP.items():
        if keyword in lower:
            return category
    return "Diğer"


class ScanRequest(BaseModel):
    base64_image: str


class ScanResponse(BaseModel):
    name: str
    category: str


@router.post("/scan", response_model=ScanResponse)
async def scan_item(request: ScanRequest):
    """
    Gönderilen base64 görüntüyü GPT-4o Vision ile analiz eder ve
    tespit edilen ürünün adını + kategorisini döner.
    """
    if not request.base64_image:
        raise HTTPException(status_code=400, detail="base64_image alanı boş olamaz.")

    try:
        item_name = await identify_item_from_base64(request.base64_image)
        category = guess_category(item_name)
        return ScanResponse(name=item_name, category=category)
    except ValueError as e:
        # API key eksik veya geçersiz — kullanılabilir hata mesajı
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sunucu hatası: {str(e)}")

