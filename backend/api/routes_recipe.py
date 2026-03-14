from fastapi import APIRouter
from schemas.api_schemas import RecipeGenerateRequest
from services.llm_service import generate_recipe_from_ingredients

router = APIRouter(prefix="/recipe", tags=["Recipe"])


@router.post("/generate")
async def generate_recipe(request: RecipeGenerateRequest):
    """
    Seçilen malzemeleri OpenAI'a yollar ve Türkçe yemek tarifi döner.
    """
    # Try-catch yok! OpenAI patlarsa veya malzeme boş gelirse Global Handler halledecek.
    recipe_text = generate_recipe_from_ingredients(request.ingredients)

    return {"status": "success", "recipe": recipe_text}
