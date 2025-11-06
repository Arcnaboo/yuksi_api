from app.utils.database import db_cursor

TABLE = "campaigns"

async def list_campaigns():
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute(f"SELECT * FROM {TABLE} ORDER BY created_at DESC;")
            return cur.fetchall(), None
    except Exception as e:
        return None, str(e)


async def get_campaign(id: str):
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute(f"SELECT * FROM {TABLE} WHERE id=%s;", (id,))
            return cur.fetchone(), None
    except Exception as e:
        return None, str(e)


async def create_campaign(title, discount_rate, rule, content, file_id):
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute(f"""
                INSERT INTO {TABLE} (title, discount_rate, rule, content, file_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *;
            """, (title, discount_rate, rule, content, file_id))
            return cur.fetchone(), None
    except Exception as e:
        return None, str(e)


async def update_campaign(id, data):
    try:
        set_clause = ", ".join([f"{k} = %({k})s" for k in data])
        data["id"] = id

        with db_cursor(dict_cursor=True) as cur:
            cur.execute(f"""
                UPDATE {TABLE}
                SET {set_clause}
                WHERE id = %(id)s
                RETURNING *;
            """, data)

            row = cur.fetchone()
            if not row:
                return False, "Record not found"
            return True, None

    except Exception as e:
        return False, str(e)


async def delete_campaign(id: str):
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute(f"DELETE FROM {TABLE} WHERE id=%s RETURNING id;", (id,))
            deleted = cur.fetchone()
            if not deleted:
                return False, "Not found"
            return True, None
    except Exception as e:
        return False, str(e)
