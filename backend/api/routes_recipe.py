from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from schemas.api_schemas import RecipeGenerateRequest
from services.llm_service import generate_recipe_stream

router = APIRouter(prefix="/recipe", tags=["Recipe"])

@router.post("/generate")
async def generate_recipe(request: RecipeGenerateRequest):
    """
    Sends the selected ingredients to OpenAI and streams back a recipe in real time (SSE).
    """
    return StreamingResponse(
        generate_recipe_stream(request.ingredients), 
        media_type="text/event-stream"
    )