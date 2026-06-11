import os
from openai import AsyncOpenAI
from typing import List
from core.api_key_store import get_api_key

# Lazy init: always fetch the latest key from api_key_store
_client = None
def _get_client() -> AsyncOpenAI:
    global _client
    api_key = get_api_key()
    if not api_key:
        raise ValueError(
            "OpenAI API key is missing. Please enter your API key "
            "in Profile > Account Settings."
        )
    if _client is None:
        _client = AsyncOpenAI(api_key=api_key)
    return _client

async def generate_recipe_stream(selected_ingredients: List[str]):
    """Generates a recipe asynchronously, yielding it chunk by chunk."""
    if not selected_ingredients:
        yield "You must select at least one ingredient to generate a recipe."
        return

    ingredients_str = ", ".join(selected_ingredients)

    prompt = (
        f"I have the following ingredients: {ingredients_str}. "
        "Please give me a practical and delicious recipe I can make using only these ingredients "
        "(plus pantry staples like salt, black pepper, oil, and water that are assumed to be available). "
        "First, write a creative name for the dish, then provide the estimated preparation time, "
        "followed by clear step-by-step instructions."
    )

    try:
        response = await _get_client().chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert chef embedded in the Mr.Fridge app. You create practical, creative, and waste-reducing recipes."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=800,
            temperature=0.7,
            stream=True  # Enable streaming mode
        )
        
        async for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    except Exception as e:
        yield f"\n[Error: {str(e)}]"