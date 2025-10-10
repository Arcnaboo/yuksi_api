import os
import io
import re
from .database import db_cursor

# -----------------------------------------------------------
# 1) Enumlar (idempotent)
# -----------------------------------------------------------
TYPE_SQL = """
DO $$ BEGIN
    CREATE TYPE doc_type AS ENUM ('license','criminal_record','vehicle_insurance');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE job_status AS ENUM ('pending','accepted','picked_up','arrived','delivered','cancelled');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
"""

# -----------------------------------------------------------
# 2) Minimal DDL (yoksa oluştur). Geo tablolar için FK eklemiyoruz.
#    Ama indexleri koyuyoruz. (FK istemezsen şimdilik daha sorunsuz.)
# -----------------------------------------------------------
DDL = """
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS drivers (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name      TEXT NOT NULL,
    last_name       TEXT NOT NULL,
    email           TEXT UNIQUE NOT NULL,
    phone           TEXT UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Geo referans tabloları
CREATE TABLE IF NOT EXISTS countries (
    id BIGINT NOT NULL,
    name VARCHAR(100) NOT NULL,
    iso3 CHAR(3),
    numeric_code CHAR(3),
    iso2 CHAR(2),
    phonecode VARCHAR(255),
    capital VARCHAR(255),
    currency VARCHAR(255),
    currency_name VARCHAR(255),
    currency_symbol VARCHAR(255),
    tld VARCHAR(255),
    native VARCHAR(255),
    population BIGINT,
    gdp BIGINT,
    region VARCHAR(255),
    region_id BIGINT,
    subregion VARCHAR(255),
    subregion_id BIGINT,
    nationality VARCHAR(255),
    timezones TEXT,
    translations TEXT,
    latitude NUMERIC(10,8),
    longitude NUMERIC(11,8),
    emoji VARCHAR(191),
    "emojiU" VARCHAR(191),
    created_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    flag SMALLINT DEFAULT 1 NOT NULL,
    "wikiDataId" VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS states (
    id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    country_id BIGINT NOT NULL,
    country_code CHAR(2) NOT NULL,
    fips_code VARCHAR(255),
    iso2 VARCHAR(255),
    iso3166_2 VARCHAR(10),
    type VARCHAR(191),
    level INT,
    parent_id BIGINT,
    native VARCHAR(255),
    latitude NUMERIC(10,8),
    longitude NUMERIC(11,8),
    timezone VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    flag SMALLINT DEFAULT 1 NOT NULL,
    "wikiDataId" VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS cities (
    id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    state_id BIGINT NOT NULL,
    state_code VARCHAR(255) NOT NULL,
    country_id BIGINT NOT NULL,
    country_code CHAR(2) NOT NULL,
    latitude NUMERIC(10,8) NOT NULL,
    longitude NUMERIC(11,8) NOT NULL,
    timezone VARCHAR(255),
    created_at TIMESTAMP DEFAULT '2014-01-01 12:01:01' NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    flag SMALLINT DEFAULT 1 NOT NULL,
    "wikiDataId" VARCHAR(255)
);

-- Uygulama tabloları
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


CREATE TABLE IF NOT EXISTS driver_onboarding (
    driver_id        UUID PRIMARY KEY REFERENCES drivers(id) ON DELETE CASCADE,
    contract_confirmed BOOLEAN,
    country_id       INT,
    working_type     INT,
    vehicle_type     INT,
    vehicle_capacity INT,
    state_id         INT,
    vehicle_year     INT,
    step             INT DEFAULT 0,
    updated_at       TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO banners (title,image_url,priority) VALUES
('Ramazan Kampanyası','https://cdn.yuksi.com/ramazan.png',1),
('Yeni Sürücü Bonusu','https://cdn.yuksi.com/bonus.png',2)
ON CONFLICT DO NOTHING;

-- Basit indexler (idempotent)
CREATE INDEX IF NOT EXISTS idx_states_country_id ON states(country_id);
CREATE INDEX IF NOT EXISTS idx_cities_state_id   ON cities(state_id);
"""

# SQL dump dosyaları burada beklenir: app/sql/10_countries.sql vb.
SQL_DIR = os.path.join(os.path.dirname(__file__), "..", "sql")

# -----------------------------------------------------------
# Yardımcılar
# -----------------------------------------------------------
def _table_exists(table_name: str) -> bool:
    from .database import db_cursor
    with db_cursor() as cur:
        cur.execute("SELECT to_regclass(%s) AS reg;", (f"public.{table_name}",))
        row = cur.fetchone()
        if row is None:
            return False
        # Hem dict (RealDictCursor) hem tuple destekle
        val = row.get("reg") if isinstance(row, dict) else row[0]
        return val is not None


def _table_rowcount(table_name: str) -> int:
    from .database import db_cursor
    if not _table_exists(table_name):
        return 0
    with db_cursor() as cur:
        cur.execute(f"SELECT COUNT(*) AS cnt FROM public.{table_name}")
        row = cur.fetchone()
        if row is None:
            return 0
        cnt = row.get("cnt") if isinstance(row, dict) else row[0]
        return int(cnt or 0)

# Dump’tan SADECE VERİ (COPY/INSERT) yükler; tüm DDL/OWNER/GRANT/SET/meta komutlarını atlar.
def _run_sql_file_data_only(path: str):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    copy_line = re.compile(r'^\s*COPY\s+.+\s+FROM\s+stdin;?\s*$', re.IGNORECASE)
    meta_line = re.compile(r'^\s*\\')  # \restrict, \connect, \., \set vb.

    skip_stmt = re.compile(
        r'^\s*(?:'
        r'CREATE\s+|DROP\s+|ALTER\s+|GRANT\s+|REVOKE\s+|OWNER\s+|SET\s+|COMMENT\s+|'
        r'SELECT\s+pg_catalog\.set_config\s*\('
        r')',
        re.IGNORECASE | re.DOTALL
    )
    insert_stmt = re.compile(r'^\s*INSERT\s+INTO\s+', re.IGNORECASE)

    with db_cursor() as cur:
        i = 0
        buf = []

        def flush_buf():
            sql = "".join(buf).strip()
            buf.clear()
            if not sql:
                return
            if insert_stmt.match(sql) and not skip_stmt.match(sql):
                cur.execute(sql)

        while i < len(lines):
            line = lines[i]

            if meta_line.match(line):
                i += 1
                continue

            if copy_line.match(line):
                copy_stmt = line.strip()
                i += 1
                data_lines = []
                while i < len(lines) and lines[i].strip() != r'\.':
                    data_lines.append(lines[i])
                    i += 1
                if i < len(lines) and lines[i].strip() == r'\.':
                    i += 1
                data = "".join(data_lines)
                flush_buf()
                cur.copy_expert(copy_stmt, io.StringIO(data))
                continue

            buf.append(line)
            if ";" in line:
                joined = "".join(buf)
                parts = joined.split(";")
                for part in parts[:-1]:
                    stmt = (part + ";").strip()
                    if insert_stmt.match(stmt) and not skip_stmt.match(stmt):
                        cur.execute(stmt)
                buf = [parts[-1]]
            i += 1

        flush_buf()

def _maybe_seed_reference_table(table: str, filename: str):
    fullpath = os.path.abspath(os.path.join(SQL_DIR, filename))
    if not os.path.exists(fullpath):
        print(f"[SEED] Skip {filename}: file not found ({fullpath})")
        return

    exists = _table_exists(table)
    rc = _table_rowcount(table)

    if not exists:
        # Tablolar DDL ile zaten oluşturuldu; gene de yoksa yeniden dener
        with db_cursor() as cur:
            cur.execute(DDL)

    if not exists or rc == 0:
        action = "creating/importing" if not exists else "importing"
        print(f"[SEED] {table}: {action} from {filename} ...")
        _run_sql_file_data_only(fullpath)
        new_rc = _table_rowcount(table)
        print(f"[SEED] {table}: rowcount={new_rc}")
    else:
        print(f"[SEED] {table}: already has {rc} rows, skipping {filename}")

# -----------------------------------------------------------
# Public API
# -----------------------------------------------------------
def init_db():
    # 1) Enumlar + 2) Minimal DDL (idempotent)
    with db_cursor() as cur:
        cur.execute(TYPE_SQL)
        cur.execute(DDL)

    # 3) Geo referans tablolarını (yoksa/doluyoksa) seed et
    _maybe_seed_reference_table("countries", "10_countries.sql")
    _maybe_seed_reference_table("states",    "20_states.sql")
    _maybe_seed_reference_table("cities",    "30_cities.sql")
