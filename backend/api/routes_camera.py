from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.vision_service import identify_item_from_base64

router = APIRouter(prefix="/camera", tags=["Camera"])

# Category guessing — simple rule-based mapping (temporary until full LLM support)
CATEGORY_MAP = {
    "milk": "Dairy", "yogurt": "Dairy", "cheese": "Dairy",
    "butter": "Dairy", "cream": "Dairy",
    "apple": "Fruit", "banana": "Fruit", "orange": "Fruit", "strawberry": "Fruit",
    "grape": "Fruit", "kiwi": "Fruit", "pear": "Fruit",
    "tomato": "Vegetable", "cucumber": "Vegetable", "pepper": "Vegetable", "broccoli": "Vegetable",
    "carrot": "Vegetable", "onion": "Vegetable", "garlic": "Vegetable", "spinach": "Vegetable",
    "chicken": "Meat & Fish", "ground beef": "Meat & Fish", "fish": "Meat & Fish",
    "sausage": "Meat & Fish", "pepperoni": "Meat & Fish",
    "egg": "Staples", "bread": "Staples", "pasta": "Staples",
    "rice": "Staples", "flour": "Staples",
    "juice": "Beverage", "soda": "Beverage", "water": "Beverage",
}


def guess_category(item_name: str) -> str:
    lower = item_name.lower()
    for keyword, category in CATEGORY_MAP.items():
        if keyword in lower:
            return category
    return "Other"


class ScanRequest(BaseModel):
    base64_image: str


class ScanResponse(BaseModel):
    name: str
    category: str


@router.post("/scan", response_model=ScanResponse)
async def scan_item(request: ScanRequest):
    """
    Analyzes the provided base64 image with GPT-4o Vision and returns
    the detected item's name and category.
    """
    if not request.base64_image:
        raise HTTPException(status_code=400, detail="base64_image field cannot be empty.")

    try:
        item_name = await identify_item_from_base64(request.base64_image)
        category = guess_category(item_name)
        return ScanResponse(name=item_name, category=category)
    except ValueError as e:
        # Missing or invalid API key — return a useful error message
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
