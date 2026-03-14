from fastapi import FastAPI
from core.database import engine, Base

# Kendi yazdığımız hata yakalayıcıları import ediyoruz
from core.exceptions import (
    MrFridgeException,
    mrfridge_exception_handler,
    global_exception_handler,
)

# Modelleri import ediyoruz ki SQLAlchemy veritabanı tablolarını oluşturabilsin
from models.house import House
from models.item import Item

# Yazdığımız kapıları (Router) import ediyoruz
# Not: routes_camera dosyasını daha önceki adımlarda tasarlamıştık.
from api.routes_inventory import router as inventory_router
from api.routes_recipe import router as recipe_router

# from api.routes_camera import router as camera_router # Bunu da eklediğini varsayıyoruz

# 1. Veritabanı tablolarını oluştur (Eğer mrfridge.db yoksa sıfırdan yaratır)
Base.metadata.create_all(bind=engine)

# 2. FastAPI Uygulamasını Başlat
app = FastAPI(
    title="Mr.Fridge API",
    description="Akıllı Envanter ve Tarif Üretme Sistemi",
    version="1.0.0",
)

# 3. Global Hata Yakalayıcıları Sisteme Kaydet
app.add_exception_handler(MrFridgeException, mrfridge_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# 4. Uç Noktaları (Router'ları) Uygulamaya Bağla
app.include_router(inventory_router)
app.include_router(recipe_router)
# app.include_router(camera_router)


@app.get("/")
async def root():
    return {"message": "Mr.Fridge Backend Sistemine Hoş Geldiniz!"}
