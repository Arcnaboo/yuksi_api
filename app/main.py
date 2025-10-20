from fastapi import FastAPI,Request,HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.routes import contact, general_setting, notification, package
from .routes import (auth, driver, jobs, payments, system, support_ticket,courier,carrier_type, geo, file, restaurant, subsection, 
                     cargotype, banner, paytr_route,order, gps_route)
from .utils.init_db import init_db
from app.utils.config import APP_ENV, get_database_url
import logging
import asyncio

logger = logging.getLogger("uvicorn.error")


'''
tags_metadata = [
    {
        "name": "CourierRegister",
        "description": "Kurye kayıt akışı (3 adım).",
        "externalDocs": {"description": "Kullanım rehberi", "url": "https://example.com/docs/courier-register"},
    },
]
'''

def setup_console_logging():
    root = logging.getLogger()
    if root.hasHandlers():
        root.handlers.clear()

    handler_console = logging.StreamHandler()
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler_console.setFormatter(fmt)
    root.addHandler(handler_console)
    root.setLevel(logging.INFO)
    logging.info("Console logging initialised")



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
app.include_router(banner.router)
app.include_router(cargotype.router)
app.include_router(courier.router)
app.include_router(driver.router)
app.include_router(file.router)
app.include_router(geo.router)
app.include_router(jobs.router)
app.include_router(payments.router)
app.include_router(paytr_route.router)
app.include_router(restaurant.router)
app.include_router(subsection.router)
app.include_router(contact.router)
app.include_router(order.router)
app.include_router(gps_route.router)
app.include_router(package.router)
app.include_router(general_setting.router)
app.include_router(notification.router)
app.include_router(carrier_type.router)
app.include_router(support_ticket.router)

setup_console_logging()

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Controller/Service içinde raise edilen HTTPException'ları tek tip JSON'a çevirir
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail, "data": {}},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Validation error on %s %s: %s", request.method, request.url, exc.errors())
    return JSONResponse(
        status_code=422,
        content={"success": False, "message": "Validation error", "errors": exc.errors(), "data": {}},
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal Server Error", "data": {}},
    )