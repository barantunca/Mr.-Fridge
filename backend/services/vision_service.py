import os
import base64
from io import BytesIO
from PIL import Image
from core.api_key_store import get_api_key, has_valid_key as _store_has_valid_key


# Check whether a valid API key is available
def _has_valid_api_key() -> bool:
    return _store_has_valid_key()


def compress_image_base64(base64_str: str, max_size: tuple = (512, 512)) -> str:
    """Resizes and optimizes an incoming Base64 image and returns it as Base64."""
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
    # Raise a meaningful error if API key is missing or a test key
    if not _has_valid_api_key():
        raise ValueError(
            "OpenAI API key is missing or invalid. "
            "Please enter a valid OPENAI_API_KEY in backend/.env."
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
                                "What is the item I am holding or focusing on in this image? "
                                "Answer with only a single word or a very short name "
                                "(e.g.: Milk, Half Apple) in English."
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
            "Invalid OpenAI API key. Please enter the correct OPENAI_API_KEY in backend/.env."
        )
    except Exception as e:
        raise Exception(f"An error occurred while processing the image: {str(e)}")