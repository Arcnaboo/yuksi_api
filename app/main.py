from fastapi import FastAPI
from .routes import auth, driver, jobs, payments, system, courier, geo, file, restaurant, subsection, cargotype,paytr_route
from .utils.init_db import init_db
from app.utils.config import APP_ENV, get_database_url
import asyncio
'''
tags_metadata = [
    {
        "name": "CourierRegister",
        "description": "Kurye kayıt akışı (3 adım).",
        "externalDocs": {"description": "Kullanım rehberi", "url": "https://example.com/docs/courier-register"},
    },
]
'''
app = FastAPI(
    title="YÜKSİ Courier API",
    version="1.0.0",
    description="Kurye uygulaması için backend API.",
    contact={"name": "YÜKSİ Tech", "email": "dev@yuksi.com"},
    license_info={"name": "Proprietary"},
    #openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.on_event("startup")
async def on_startup():
    print(f"[BOOT] APP_ENV={APP_ENV}")
    print(f"[BOOT] DB_URL={(get_database_url()).split('@')[-1]}")  # host/db kısmını gösterir
    try:
        result = init_db()
        if asyncio.iscoroutine(result):
            await result
        print("[BOOT] init_db tamam")
    except Exception as e:
        # Başlangıçta veritabanı init hatasını görünür kılalım
        print(f"[BOOT][ERROR] init_db başarısız: {e}")
        raise

app.include_router(system.router)

app.include_router(auth.router)
app.include_router(cargotype.router)
app.include_router(courier.router)
app.include_router(driver.router)
app.include_router(file.router)
app.include_router(geo.router)
app.include_router(jobs.router)
app.include_router(payments.router)
app.include_router(restaurant.router)
app.include_router(subsection.router)
app.include_router(paytr_route.router)