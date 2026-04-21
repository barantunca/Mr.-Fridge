import os
import base64
from io import BytesIO
from PIL import Image
from core.api_key_store import get_api_key, has_valid_key as _store_has_valid_key


# Geçerli bir API key var mı kontrol et
def _has_valid_api_key() -> bool:
    return _store_has_valid_key()


def compress_image_base64(base64_str: str, max_size: tuple = (512, 512)) -> str:
    """Gelen Base64 görüntüyü küçültüp optimize ederek geri döndürür."""
    try:
        image_data = base64.b64decode(base64_str)
        img = Image.open(BytesIO(image_data))
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        buffered = BytesIO()
        img.convert("RGB").save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode("utf-8")
    except Exception:
        return base64_str


async def identify_item_from_base64(base64_image: str) -> str:
    # API key yoksa veya test key'i ise anlamlı hata ver
    if not _has_valid_api_key():
        raise ValueError(
            "OpenAI API key eksik veya geçersiz. "
            "backend/.env dosyasına gerçek OPENAI_API_KEY değerini girin."
        )

    from openai import AsyncOpenAI, AuthenticationError

    client = AsyncOpenAI(api_key=get_api_key())

    try:
        optimized_base64 = compress_image_base64(base64_image)

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Bu resimde elimde tuttuğum veya odaklanılan eşya nedir? "
                                "Sadece tek bir kelime veya çok kısa bir isimle "
                                "(örneğin: Süt, Yarım Elma) Türkçe olarak cevap ver."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{optimized_base64}",
                                "detail": "low",
                            },
                        },
                    ],
                }
            ],
            max_tokens=30,
        )
        return response.choices[0].message.content.strip()

    except AuthenticationError:
        raise ValueError(
            "OpenAI API key geçersiz. backend/.env dosyasına doğru OPENAI_API_KEY girin."
        )
    except Exception as e:
        raise Exception(f"Görüntü işlenirken bir hata oluştu: {str(e)}")