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


DO $$ BEGIN
    CREATE TYPE courier_doc_type AS ENUM (
        'VergiLevhasi',
        'EhliyetOn',
        'EhliyetArka',
        'RuhsatOn',
        'RuhsatArka',
        'KimlikOn',
        'KimlikArka'
    );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE content_type AS ENUM (
        'Destek',
        'Hakkimizda',
        'Iletisim',
        'GizlilikPolitikasi',
        'KullanimKosullari',
        'KuryeGizlilikSözlesmesi',
        'KuryeTasiyiciSözlesmesi'
    );
    CREATE TYPE delivery_type AS ENUM ('yerinde', 'paket_servis', 'gel_al');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE order_status AS ENUM ('iptal', 'hazirlaniyor', 'kurye_cagrildi', 'kuryeye_verildi', 'yolda', 'teslim_edildi');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE courier_document_status AS ENUM ('evrak_bekleniyor', 'inceleme_bekleniyor', 'eksik_belge', 'reddedildi', 'onaylandi');
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
    is_active       BOOLEAN DEFAULT FALSE,
    deleted         BOOLEAN DEFAULT FALSE,
    deleted_at      TIMESTAMPTZ,
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

CREATE TABLE IF NOT EXISTS files (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID,
    image_url       TEXT,
    size            INT,
    mime_type       TEXT,
    filename        TEXT,
    key             TEXT,
    uploaded_at     TIMESTAMPTZ DEFAULT NOW(),
    delated_at      TIMESTAMPTZ,
    is_deleted      BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS courier_documents (
  id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id    UUID NOT NULL REFERENCES drivers(id) ON DELETE CASCADE,
  file_id    UUID NOT NULL REFERENCES files(id)   ON DELETE RESTRICT,
  doc_type   courier_doc_type NOT NULL,
  courier_document_status courier_document_status NOT NULL DEFAULT 'inceleme_bekleniyor',
  created_at TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
  UNIQUE (user_id, doc_type)
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


CREATE TABLE IF NOT EXISTS restaurants (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           TEXT UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    phone           TEXT NOT NULL,
    country_id      BIGINT,
    name            TEXT NOT NULL,
    contact_person  TEXT,
    tax_number      TEXT,
    address_line1   TEXT,
    address_line2   TEXT,
    state_id        BIGINT,
    city_id         BIGINT,
    opening_hour    TIME,
    closing_hour    TIME,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS refresh_tokens (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  user_type TEXT NOT NULL, 
  token TEXT NOT NULL UNIQUE,
  expires_at TIMESTAMPTZ NOT NULL,
  revoked_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS contact_messages (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    subject TEXT,
    message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS subsections (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content_type content_type NOT NULL,
    show_in_menu BOOLEAN DEFAULT FALSE,
    show_in_footer BOOLEAN DEFAULT FALSE,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    restaurant_id UUID REFERENCES restaurants(id) ON DELETE CASCADE,
    courier_id UUID REFERENCES drivers(id) ON DELETE SET NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    customer TEXT NOT NULL,
    phone TEXT NOT NULL,
    address TEXT NOT NULL,
    delivery_address TEXT NOT NULL,
    type delivery_type NOT NULL,
    status order_status DEFAULT 'hazirlaniyor',
    amount DECIMAL(10,2) NOT NULL,
    carrier_type TEXT DEFAULT 'kurye',
    vehicle_type TEXT DEFAULT '2_teker_motosiklet',
    cargo_type TEXT,
    special_requests TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    product_name TEXT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    quantity INTEGER NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS system_admins (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name      TEXT NOT NULL,
    last_name      TEXT NOT NULL,
    email          TEXT UNIQUE NOT NULL,
    password_hash  TEXT NOT NULL,
    created_at     TIMESTAMPTZ DEFAULT NOW(),
    singleton      SMALLINT DEFAULT 1 UNIQUE
);

CREATE TABLE IF NOT EXISTS packages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    carrier TEXT NOT NULL,
    days INT NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS general_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    app_name TEXT NOT NULL,
    app_title TEXT NOT NULL,
    keywords TEXT NOT NULL,
    email TEXT NOT NULL,
    whatsapp TEXT NOT NULL,
    address TEXT NOT NULL,
    map_embed_code TEXT NOT NULL,
    logo_path TEXT, 
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    type TEXT NOT NULL, -- single veya bulk
    target_email TEXT,
    user_type TEXT,     -- courier, restaurant, all
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS carrier_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    start_km INT NOT NULL,
    start_price NUMERIC(10,2) NOT NULL,
    km_price NUMERIC(10,2) NOT NULL,
    image_file_id UUID REFERENCES files(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS support_tickets (
    id SERIAL PRIMARY KEY,
    restaurant_id UUID REFERENCES restaurants(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    restaurant_name TEXT NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    reply TEXT,
    status TEXT DEFAULT 'pending', 
    created_at TIMESTAMPTZ DEFAULT NOW(),
    replied_at TIMESTAMPTZ
);


CREATE TABLE IF NOT EXISTS city_prices (
    id SERIAL PRIMARY KEY,
    route_name TEXT NOT NULL,
    country_id INT NOT NULL,
    state_id INT NOT NULL,
    city_id INT NOT NULL,
    courier_price NUMERIC(10,2) NOT NULL,
    minivan_price NUMERIC(10,2) NOT NULL,
    panelvan_price NUMERIC(10,2) NOT NULL,
    kamyonet_price NUMERIC(10,2) NOT NULL,
    kamyon_price NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);



CREATE TABLE IF NOT EXISTS courier_ratings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    restaurant_id UUID REFERENCES restaurants(id) ON DELETE CASCADE,
    courier_id UUID REFERENCES drivers(id) ON DELETE CASCADE,
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(restaurant_id, courier_id, order_id)
);

CREATE TABLE IF NOT EXISTS gps_table (
    driver_id UUID PRIMARY KEY REFERENCES drivers(id) ON DELETE CASCADE,
    latitude NUMERIC(10,6) NOT NULL,
    longitude NUMERIC(10,6) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_gps_updated_at ON gps_table(updated_at DESC);

-- Basit indexler (idempotent)
CREATE INDEX IF NOT EXISTS idx_states_country_id ON states(country_id);
CREATE INDEX IF NOT EXISTS idx_cities_state_id   ON cities(state_id);
CREATE INDEX IF NOT EXISTS idx_orders_restaurant_id ON orders(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_orders_courier_id ON orders(courier_id);
CREATE INDEX IF NOT EXISTS idx_orders_code ON orders(code);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_courier_ratings_restaurant_id ON courier_ratings(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_courier_ratings_courier_id ON courier_ratings(courier_id);
CREATE INDEX IF NOT EXISTS idx_courier_ratings_order_id ON courier_ratings(order_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user ON refresh_tokens(user_id, user_type);
CREATE INDEX IF NOT EXISTS ix_banners_active ON banners(active);
CREATE INDEX IF NOT EXISTS ix_banners_priority ON banners(priority DESC);
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
