from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.database import engine, Base

# Kendi yazdığımız hata yakalayıcıları import ediyoruz
from core.exceptions import (
    MrFridgeException,
    mrfridge_exception_handler,
    global_exception_handler,
)

# Modelleri import ediyoruz
from models.fridge import Fridge
from models.item import Item

# Yazdığımız kapıları (Router) import ediyoruz
from api.routes_inventory import router as inventory_router
from api.routes_recipe import router as recipe_router
from api.routes_camera import router as camera_router
from api.routes_settings import router as settings_router

# Asenkron Tablo Oluşturma (Lifespan mantığı)
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

# FastAPI Uygulamasını Başlat
app = FastAPI(
    title="Mr.Fridge API",
    description="Akıllı Envanter ve Tarif Üretme Sistemi (Performans Sürümü)",
    version="1.1.0",
    lifespan=lifespan
)

# Global Hata Yakalayıcıları Sisteme Kaydet
app.add_exception_handler(MrFridgeException, mrfridge_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Uç Noktaları (Router'ları) Uygulamaya Bağla
app.include_router(inventory_router)
app.include_router(recipe_router)
app.include_router(camera_router)
app.include_router(settings_router)

@app.get("/")
async def root():
    return {"message": "Mr.Fridge Backend Sistemine Hoş Geldiniz! (Asenkron Sürüm Aktif)"}