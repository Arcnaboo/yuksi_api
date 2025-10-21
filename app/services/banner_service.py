from typing import Any, Dict, Tuple, Optional, List
from uuid import UUID
import uuid
from app.utils.database_async import fetch_one, fetch_all, execute
from app.utils.database import db_cursor

async def get_all_banners() -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    with db_cursor(dict_cursor=True) as cur:
        cur.execute("""
            SELECT id, title, image_url, priority, active
            FROM banners
            ORDER BY active DESC, priority DESC, title ASC
        """)
        rows = cur.fetchall()
        if not rows:
            return None, "Banners not found"
        return rows, None

async def get_banner_by_id(banner_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        uuid.UUID(str(banner_id))
    except ValueError:
        return None, "Invalid ID"
    query = """
        SELECT id, title, image_url, priority, active
        FROM banners
        WHERE id = $1
    """
    row = await fetch_one(query, banner_id)
    if not row:
        return None, "Banner not found"
    return dict(row), None

async def create_banner(
    title: str,
    image_url: str,
    priority: int = 0,
    active: bool = True
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    with db_cursor(dict_cursor=True) as cur:
        cur.execute("""
            INSERT INTO banners (title, image_url, priority, active)
            VALUES (%s, %s, %s, %s)
            RETURNING id, title, image_url, priority, active
        """, (title, image_url, priority, active))
        row = cur.fetchone()
        return row, None

async def update_banner(
    banner_id: str,
    title: str,
    image_url: str,
    priority: int = 0,
    active: bool = True
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        uuid.UUID(str(banner_id))
    except ValueError:
        return None, "Invalid ID"
    query = """
        UPDATE banners
        SET title = $1,
            image_url = $2,
            priority = $3,
            active = $4
        WHERE id = $5
        RETURNING id, title, image_url, priority, active
    """
    row = await fetch_one(query, title, image_url, priority, active, banner_id)
    if not row:
        return None, "Banner not found"
    return dict(row), None

async def delete_banner(banner_id: UUID) -> Optional[str]:
    try:
        uuid.UUID(str(banner_id))
    except ValueError:
        return "Invalid ID"
    query = "DELETE FROM banners WHERE id = $1 RETURNING id"
    row = await fetch_one(query, banner_id)
    if not row:
        return "Banner not found"
    return "Banner deleted successfully"
