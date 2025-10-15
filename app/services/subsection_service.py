from typing import Any, Dict, Optional, Tuple, List
from app.utils.database import db_cursor

# ✅ ENUM MAP
CONTENT_TYPE_MAP = {
    1: "Destek",
    2: "Hakkimizda",
    3: "Iletisim",
    4: "GizlilikPolitikasi",
    5: "KullanimKosullari",
    6: "KuryeGizlilikSözlesmesi",
    7: "KuryeTasiyiciSözlesmesi"
}

async def create_subsection(
    title: str,
    content_type: int,   # INT GELECEK — MAPE ÇEVİRİYORUZ
    show_in_menu: bool,
    show_in_footer: bool,
    content: str
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        ct_value = CONTENT_TYPE_MAP.get(int(content_type))
        if not ct_value:
            return None, f"Geçersiz content_type değeri! ({content_type})"

        with db_cursor() as cur:
            cur.execute(
                """
                INSERT INTO subsections (title, content_type, show_in_menu, show_in_footer, content)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, title, content_type, show_in_menu, show_in_footer, content, created_at;
                """,
                (title, ct_value, show_in_menu, show_in_footer, content)
            )
            row = cur.fetchone()
            return row, None
    except Exception as e:
        return None, str(e)


async def get_all_subsections(limit: int = 100, offset: int = 0) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    try:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT id, title, content_type, show_in_menu, show_in_footer, content, created_at
                FROM subsections
                ORDER BY id DESC
                LIMIT %s OFFSET %s;
                """,
                (limit, offset)
            )
            rows = cur.fetchall()
            return rows, None
    except Exception as e:
        return None, str(e)


async def get_subsection_by_id(sub_id: int) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT id, title, content_type, show_in_menu, show_in_footer, content, created_at
                FROM subsections
                WHERE id = %s;
                """,
                (sub_id,)
            )
            row = cur.fetchone()
            return row, None
    except Exception as e:
        return None, str(e)


async def update_subsection(sub_id: int, fields: Dict[str, Any]) -> Optional[str]:
    try:
        if not fields:
            return "Güncellenecek alan yok"

        # ✅ ENUM GÜNCELLEMEDE DE MAP KONTROLÜ
        if "content_type" in fields:
            ct_value = CONTENT_TYPE_MAP.get(int(fields["content_type"]))
            if not ct_value:
                return f"Geçersiz content_type değeri! ({fields['content_type']})"
            fields["content_type"] = ct_value

        set_clauses = []
        values = []
        for key, value in fields.items():
            set_clauses.append(f"{key} = %s")
            values.append(value)

        values.append(sub_id)

        sql = f"""
            UPDATE subsections
            SET {", ".join(set_clauses)}
            WHERE id = %s;
        """

        with db_cursor() as cur:
            cur.execute(sql, tuple(values))
            return None
    except Exception as e:
        return str(e)


async def delete_subsection(sub_id: int) -> Optional[str]:
    try:
        with db_cursor() as cur:
            cur.execute("DELETE FROM subsections WHERE id = %s;", (sub_id,))
            return None
    except Exception as e:
        return str(e)
