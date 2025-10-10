from fastapi import FastAPI
from .routes import auth, driver, jobs, payments, system, courier,geo
from .utils.init_db import init_db

tags_metadata = [
    {
        "name": "CourierRegister",
        "description": "Kurye kayıt akışı (3 adım).",
        "externalDocs": {"description": "Kullanım rehberi", "url": "https://example.com/docs/courier-register"},
    },
]

app = FastAPI(
    title="YÜKSİ Courier API",
    version="1.0.0",
    description="Kurye uygulaması için backend API.",
    contact={"name": "YÜKSİ Tech", "email": "dev@yuksi.com"},
    license_info={"name": "Proprietary"},
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(auth.router)
app.include_router(driver.router)
app.include_router(jobs.router)
app.include_router(payments.router)
app.include_router(system.router)
app.include_router(courier.router)
app.include_router(geo.router)