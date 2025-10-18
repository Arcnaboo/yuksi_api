from typing import Any, Dict, Optional, Tuple, List
from app.utils.database_async import fetch_one, fetch_all, execute

# === ENUM MAP ===
CONTENT_TYPE_MAP = {
    1: "Destek",
    2: "Hakkimizda",
    3: "Iletisim",
    4: "GizlilikPolitikasi",
    5: "KullanimKosullari",
    6: "KuryeGizlilikSözlesmesi",
    7: "KuryeTasiyiciSözlesmesi",
}

# === YARDIMCI FORMATLAYICI ===
def format_subsection_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "title": row["title"],
        "content_type": row["content_type"],
        "show_in_menu": row["show_in_menu"],
        "show_in_footer": row["show_in_footer"],
        "content": row["content"],
        "created_at": row["created_at"],
    }


# === CREATE ===
async def create_subsection(
    title: str,
    content_type: int,
    show_in_menu: bool,
    show_in_footer: bool,
    content: str,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        ct_value = CONTENT_TYPE_MAP.get(int(content_type))
        if not ct_value:
            return None, f"Geçersiz content_type değeri! ({content_type})"

        query = """
            INSERT INTO subsections (title, content_type, show_in_menu, show_in_footer, content)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, title, content_type, show_in_menu, show_in_footer, content, created_at;
        """
        row = await fetch_one(query, title, ct_value, show_in_menu, show_in_footer, content)
        if not row:
            return None, "Insert failed"

        return format_subsection_row(row), None

    except Exception as e:
        return None, str(e)


# === GET ALL ===
async def get_all_subsections(limit: int = 100, offset: int = 0) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    try:
        query = """
            SELECT id, title, content_type, show_in_menu, show_in_footer, content, created_at
            FROM subsections
            ORDER BY id DESC
            LIMIT $1 OFFSET $2;
        """
        rows = await fetch_all(query, limit, offset)
        if not rows:
            return [], None
        return [format_subsection_row(r) for r in rows], None
    except Exception as e:
        return None, str(e)


# === GET BY ID ===
async def get_subsection_by_id(sub_id: int) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        query = """
            SELECT id, title, content_type, show_in_menu, show_in_footer, content, created_at
            FROM subsections
            WHERE id = $1;
        """
        row = await fetch_one(query, sub_id)
        if not row:
            return None, "SubSection bulunamadı"
        return format_subsection_row(row), None
    except Exception as e:
        return None, str(e)


# === UPDATE ===
async def update_subsection(sub_id: int, fields: Dict[str, Any]) -> Optional[str]:
    try:
        if not fields:
            return "Güncellenecek alan yok"

        if "content_type" in fields:
            ct_value = CONTENT_TYPE_MAP.get(int(fields["content_type"]))
            if not ct_value:
                return f"Geçersiz content_type değeri! ({fields['content_type']})"
            fields["content_type"] = ct_value

        set_clauses = []
        values = []
        i = 1
        for key, value in fields.items():
            set_clauses.append(f"{key} = ${i}")
            values.append(value)
            i += 1

        query = f"""
            UPDATE subsections
            SET {', '.join(set_clauses)}
            WHERE id = ${i};
        """
        values.append(sub_id)
        await execute(query, *values)
        return None
    except Exception as e:
        return str(e)


# === DELETE ===
async def delete_subsection(sub_id: int) -> Optional[str]:
    try:
        query = "DELETE FROM subsections WHERE id = $1;"
        await execute(query, sub_id)
        return None
    except Exception as e:
        return str(e)
