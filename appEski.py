# -----------------------------------------------------------
#  YÜKSİ  –  Courier Driver Backend
#  Single-file FastAPI backend
#  uvicorn app:app --reload
# -----------------------------------------------------------
#  ENV VARS
#   DATABASE_URL=postgresql://user:password@db:5432/yuksi
#   JWT_SECRET_KEY=super-secret-jwt-key-min-32-chars
#   JWT_ALGORITHM=HS256
# -----------------------------------------------------------

import os
import datetime
from typing import List, Optional

import bcrypt
import psycopg2
import psycopg2.extras
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel, EmailStr

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
if not all([DATABASE_URL, JWT_SECRET_KEY]):
    raise RuntimeError("DATABASE_URL and JWT_SECRET_KEY must be set")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
app = FastAPI(title="YÜKSİ Courier API", version="1.0.0")

# ------------------------------------------------------------------
# DB helpers
# ------------------------------------------------------------------
def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    # 1.  create types safely (PG 15 compatible)
    type_sql = """
    DO $$ BEGIN
        CREATE TYPE doc_type AS ENUM ('license','criminal_record','vehicle_insurance');
    EXCEPTION WHEN duplicate_object THEN NULL;
    END $$;

    DO $$ BEGIN
        CREATE TYPE job_status AS ENUM ('pending','accepted','picked_up','arrived','delivered','cancelled');
    EXCEPTION WHEN duplicate_object THEN NULL;
    END $$;
    """

    # 2.  the rest of your schema (unchanged)
    ddl = """
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    CREATE TABLE IF NOT EXISTS drivers (
        id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        full_name       TEXT NOT NULL,
        email           TEXT UNIQUE NOT NULL,
        phone           TEXT UNIQUE NOT NULL,
        password_hash   TEXT NOT NULL,
        created_at      TIMESTAMPTZ DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS vehicles (
        id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        driver_id       UUID REFERENCES drivers(id) ON DELETE CASCADE,
        make            TEXT,
        model           TEXT,
        year            INT,
        plate           TEXT UNIQUE,
        created_at      TIMESTAMPTZ DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS documents (
        id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        driver_id       UUID REFERENCES drivers(id) ON DELETE CASCADE,
        doc_type        doc_type,
        file_url        TEXT,
        uploaded_at     TIMESTAMPTZ DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS driver_status (
        driver_id       UUID PRIMARY KEY REFERENCES drivers(id) ON DELETE CASCADE,
        online          BOOLEAN DEFAULT FALSE,
        updated_at      TIMESTAMPTZ DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS jobs (
        id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        customer_name   TEXT,
        customer_phone  TEXT,
        pickup_address  TEXT,
        drop_address    TEXT,
        price           NUMERIC(10,2),
        status          job_status DEFAULT 'pending',
        driver_id       UUID REFERENCES drivers(id),
        created_at      TIMESTAMPTZ DEFAULT NOW(),
        updated_at      TIMESTAMPTZ DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS payments (
        id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        job_id          UUID REFERENCES jobs(id),
        amount          NUMERIC(10,2),
        status          TEXT DEFAULT 'pending',
        created_at      TIMESTAMPTZ DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS banners (
        id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        title           TEXT,
        image_url       TEXT,
        priority        INT DEFAULT 0,
        active          BOOLEAN DEFAULT TRUE
    );

    INSERT INTO banners (title,image_url,priority) VALUES
    ('Ramazan Kampanyası','https://cdn.yuksi.com/ramazan.png',1),
    ('Yeni Sürücü Bonusu','https://cdn.yuksi.com/bonus.png',2)
    ON CONFLICT DO NOTHING;
    """

    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(type_sql)   # create types first
            cur.execute(ddl)        # then everything else
        conn.commit()
# Run once at cold-start
init_db()

# ------------------------------------------------------------------
# Pydantic models
# ------------------------------------------------------------------
class RegisterReq(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password: str

class LoginReq(BaseModel):
    email: EmailStr
    password: str

class VehicleReq(BaseModel):
    make: str
    model: str
    year: int
    plate: str

class JobStatusUpdateReq(BaseModel):
    job_id: str
    status: str  # picked_up | arrived | delivered

# ------------------------------------------------------------------
# Auth helpers
# ------------------------------------------------------------------
def hash_pwd(pwd: str) -> str:
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def verify_pwd(pwd: str, hashed: str) -> bool:
    return bcrypt.checkpw(pwd.encode(), hashed.encode())

def create_jwt(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def get_current_driver(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        driver_id: str = payload.get("sub")
        if driver_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT id,full_name,email,phone FROM drivers WHERE id=%s", (driver_id,))
        driver = cur.fetchone()
    if driver is None:
        raise credentials_exception
    return driver

# ------------------------------------------------------------------
# Auth endpoints
# ------------------------------------------------------------------
@app.post("/register")
def register(req: RegisterReq, db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("SELECT id FROM drivers WHERE email=%s OR phone=%s", (req.email, req.phone))
        if cur.fetchone():
            return {"success": False, "message": "Email or phone already registered", "data": {}}
        hashed = hash_pwd(req.password)
        cur.execute(
            "INSERT INTO drivers (full_name,email,phone,password_hash) VALUES (%s,%s,%s,%s) RETURNING id",
            (req.full_name, req.email, req.phone, hashed),
        )
        driver_id = cur.fetchone()[0]
        cur.execute("INSERT INTO driver_status (driver_id) VALUES (%s)", (driver_id,))
    db.commit()
    token = create_jwt({"sub": str(driver_id)})
    return {"success": True, "message": "Driver registered", "data": {"access_token": token, "token_type": "bearer"}}

@app.post("/login")
def login(req: LoginReq, db=Depends(get_db)):
    with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT id,password_hash FROM drivers WHERE email=%s", (req.email,))
        row = cur.fetchone()
        if not row or not verify_pwd(req.password, row["password_hash"]):
            return {"success": False, "message": "Wrong email or password", "data": {}}
    token = create_jwt({"sub": str(row["id"])})
    return {"success": True, "message": "Login successful", "data": {"access_token": token, "token_type": "bearer"}}

@app.get("/me")
def me(driver=Depends(get_current_driver)):
    return {"success": True, "message": "Driver info", "data": driver}

# ------------------------------------------------------------------
# Driver Profile
# ------------------------------------------------------------------
@app.post("/driver/vehicle")
def save_vehicle(req: VehicleReq, driver=Depends(get_current_driver), db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute(
            """INSERT INTO vehicles (driver_id,make,model,year,plate)
               VALUES (%s,%s,%s,%s,%s)
               ON CONFLICT (driver_id) DO UPDATE
               SET make=EXCLUDED.make, model=EXCLUDED.model, year=EXCLUDED.year, plate=EXCLUDED.plate
            """,
            (driver["id"], req.make, req.model, req.year, req.plate),
        )
    db.commit()
    return {"success": True, "message": "Vehicle saved", "data": {}}

@app.post("/driver/documents/upload")
def upload_docs(
    license: Optional[UploadFile] = File(None),
    criminal_record: Optional[UploadFile] = File(None),
    vehicle_insurance: Optional[UploadFile] = File(None),
    driver=Depends(get_current_driver),
    db=Depends(get_db),
):
    # In production upload to S3 / Supabase Storage and save URL
    # Here we simulate by storing fake URLs
    base = "https://cdn.yuksi.com/docs"
    with db.cursor() as cur:
        if license:
            url = f"{base}/{driver['id']}_license.pdf"
            cur.execute(
                "INSERT INTO documents (driver_id,doc_type,file_url) VALUES (%s,'license',%s) ON CONFLICT DO NOTHING",
                (driver["id"], url),
            )
        if criminal_record:
            url = f"{base}/{driver['id']}_criminal.pdf"
            cur.execute(
                "INSERT INTO documents (driver_id,doc_type,file_url) VALUES (%s,'criminal_record',%s) ON CONFLICT DO NOTHING",
                (driver["id"], url),
            )
        if vehicle_insurance:
            url = f"{base}/{driver['id']}_insurance.pdf"
            cur.execute(
                "INSERT INTO documents (driver_id,doc_type,file_url) VALUES (%s,'vehicle_insurance',%s) ON CONFLICT DO NOTHING",
                (driver["id"], url),
            )
    db.commit()
    return {"success": True, "message": "Documents uploaded", "data": {}}

@app.get("/driver/documents")
def list_docs(driver=Depends(get_current_driver), db=Depends(get_db)):
    with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT doc_type,file_url,uploaded_at FROM documents WHERE driver_id=%s", (driver["id"],))
        rows = cur.fetchall()
    return {"success": True, "message": "Documents list", "data": rows}

@app.post("/driver/profile/submit")
def finalize_profile(driver=Depends(get_current_driver), db=Depends(get_db)):
    # Check minimum requirements
    with db.cursor() as cur:
        cur.execute("SELECT id FROM vehicles WHERE driver_id=%s", (driver["id"],))
        if not cur.fetchone():
            return {"success": False, "message": "Vehicle info missing", "data": {}}
        cur.execute("SELECT COUNT(*) FROM documents WHERE driver_id=%s", (driver["id"],))
        if cur.fetchone()[0] < 2:
            return {"success": False, "message": "Upload at least license and criminal record", "data": {}}
    return {"success": True, "message": "Profile submitted for approval", "data": {}}

# ------------------------------------------------------------------
# Driver Status
# ------------------------------------------------------------------
@app.post("/driver/status/online")
def go_online(driver=Depends(get_current_driver), db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute(
            "INSERT INTO driver_status (driver_id,online) VALUES (%s,TRUE) ON CONFLICT (driver_id) DO UPDATE SET online=TRUE, updated_at=NOW()",
            (driver["id"],),
        )
    db.commit()
    return {"success": True, "message": "You are online", "data": {}}

@app.post("/driver/status/offline")
def go_offline(driver=Depends(get_current_driver), db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute(
            "UPDATE driver_status SET online=FALSE, updated_at=NOW() WHERE driver_id=%s", (driver["id"],)
        )
    db.commit()
    return {"success": True, "message": "You are offline", "data": {}}

@app.get("/driver/earnings")
def earnings(driver=Depends(get_current_driver), db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute(
            "SELECT COALESCE(SUM(price),0) FROM jobs WHERE driver_id=%s AND status='delivered'", (driver["id"],)
        )
        total = cur.fetchone()[0]
    return {"success": True, "message": "Total earnings", "data": {"total_earnings": float(total)}}

@app.get("/banners")
def banners(db=Depends(get_db)):
    with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT title,image_url FROM banners WHERE active=TRUE ORDER BY priority DESC")
        rows = cur.fetchall()
    return {"success": True, "message": "Banners", "data": rows}

# ------------------------------------------------------------------
# Jobs
# ------------------------------------------------------------------
@app.get("/driver/jobs/available")
def available_jobs(driver=Depends(get_current_driver), db=Depends(get_db)):
    with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """SELECT id,customer_name,customer_phone,pickup_address,drop_address,price
               FROM jobs
               WHERE status='pending'
               ORDER BY created_at DESC
            """
        )
        rows = cur.fetchall()
    return {"success": True, "message": "Available jobs", "data": rows}

@app.post("/driver/jobs/accept")
def accept_job(job_id: str = Form(...), driver=Depends(get_current_driver), db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute(
            "UPDATE jobs SET status='accepted', driver_id=%s, updated_at=NOW() WHERE id=%s AND status='pending'",
            (driver["id"], job_id),
        )
        if cur.rowcount == 0:
            return {"success": False, "message": "Job no longer available", "data": {}}
    db.commit()
    return {"success": True, "message": "Job accepted", "data": {}}

@app.post("/driver/jobs/update")
def update_job(req: JobStatusUpdateReq, driver=Depends(get_current_driver), db=Depends(get_db)):
    allowed = {"picked_up", "arrived", "delivered"}
    if req.status not in allowed:
        return {"success": False, "message": "Invalid status", "data": {}}
    with db.cursor() as cur:
        cur.execute(
            "UPDATE jobs SET status=%s, updated_at=NOW() WHERE id=%s AND driver_id=%s",
            (req.status, req.job_id, driver["id"]),
        )
        if cur.rowcount == 0:
            return {"success": False, "message": "Job not found or not yours", "data": {}}
    db.commit()
    return {"success": True, "message": "Job updated", "data": {}}

@app.get("/driver/jobs")
def my_jobs(driver=Depends(get_current_driver), db=Depends(get_db)):
    with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """SELECT id,customer_name,customer_phone,pickup_address,drop_address,price,status,created_at
               FROM jobs
               WHERE driver_id=%s
               ORDER BY created_at DESC
            """,
            (driver["id"],),
        )
        rows = cur.fetchall()
    return {"success": True, "message": "My jobs", "data": rows}

# ------------------------------------------------------------------
# Payments
# ------------------------------------------------------------------
@app.post("/payments/start")
def start_payment(job_id: str = Form(...), driver=Depends(get_current_driver), db=Depends(get_db)):
    # Simulate payment provider session
    with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT price FROM jobs WHERE id=%s AND driver_id=%s", (job_id, driver["id"]))
        row = cur.fetchone()
        if not row:
            return {"success": False, "message": "Job not found", "data": {}}
        amount = row["price"]
        cur.execute(
            "INSERT INTO payments (job_id,amount) VALUES (%s,%s) ON CONFLICT (job_id) DO UPDATE SET amount=EXCLUDED.amount RETURNING id",
            (job_id, amount),
        )
        payment_id = cur.fetchone()["id"]
    db.commit()
    return {
        "success": True,
        "message": "Payment session started",
        "data": {"payment_id": payment_id, "redirect_url": f"https://fake-payment.com/{payment_id}"},
    }

@app.get("/payments/status")
def payment_status(payment_id: str, driver=Depends(get_current_driver), db=Depends(get_db)):
    with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """SELECT p.id,p.status,p.amount,j.id as job_id
               FROM payments p
               JOIN jobs j ON j.id=p.job_id
               WHERE p.id=%s AND j.driver_id=%s
            """,
            (payment_id, driver["id"]),
        )
        row = cur.fetchone()
        if not row:
            return {"success": False, "message": "Payment not found", "data": {}}
    return {"success": True, "message": "Payment status", "data": dict(row)}

# ------------------------------------------------------------------
# System
# ------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}