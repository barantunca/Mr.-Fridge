import os
import base64
from io import BytesIO
from PIL import Image
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

# Asenkron OpenAI istemcisi
client = AsyncOpenAI(api_key=API_KEY)

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
        # Eğer hatalı bir görsel gelirse orijinalini döndür
        return base64_str

async def identify_item_from_base64(base64_image: str) -> str:
    try:
        # Görüntüyü sıkıştır (Ağ tasarrufu ve hız)
        optimized_base64 = compress_image_base64(base64_image)
        
        # Asenkron olarak OpenAI API'sine istek at
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Bu resimde elimde tuttuğum veya odaklanılan eşya nedir? Sadece tek bir kelime veya çok kısa bir isimle (örneğin: Süt, Yarım Elma) Türkçe olarak cevap ver."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{optimized_base64}", "detail": "low"}},
                    ],
                }
            ],
            max_tokens=30,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        raise Exception(f"Görüntü işlenirken bir hata oluştu: {str(e)}")