import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)


def identify_item_from_base64(base64_image: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Bu resimde elimde tuttuğum veya odaklanılan eşya nedir? Sadece tek bir kelime veya çok kısa bir isimle (örneğin: Süt, Yarım Elma, Ketçap Şişesi) Türkçe olarak cevap ver.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=50,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        raise Exception(f"Görüntü işlenirken bir hata oluştu: {str(e)}")
