from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.database import engine, Base

# Import our custom exception handlers
from core.exceptions import (
    MrFridgeException,
    mrfridge_exception_handler,
    global_exception_handler,
)

# Import database models
from models.fridge import Fridge
from models.item import Item

# Import API routers
from api.routes_inventory import router as inventory_router
from api.routes_recipe import router as recipe_router
from api.routes_camera import router as camera_router
from api.routes_settings import router as settings_router

# Async table creation (Lifespan pattern)
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

# Initialize FastAPI application
app = FastAPI(
    title="Mr.Fridge API",
    description="Smart Inventory & Recipe Generation System",
    version="1.1.0",
    lifespan=lifespan
)

# Register global exception handlers
app.add_exception_handler(MrFridgeException, mrfridge_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Mount routers
app.include_router(inventory_router)
app.include_router(recipe_router)
app.include_router(camera_router)
app.include_router(settings_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Mr.Fridge Backend! (Async Version Active)"}