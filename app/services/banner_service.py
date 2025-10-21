from typing import Any, Dict, Tuple, Optional, List
from uuid import UUID
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
    with db_cursor(dict_cursor=True) as cur:
        cur.execute("""
            SELECT id, title, image_url, priority, active
            FROM banners
            WHERE id = %s
        """, (banner_id))
        row = cur.fetchone()
        if not row:
            return None, "Banner not found"
        return row, None
    
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
    with db_cursor(dict_cursor=True) as cur:
        cur.execute("""
            UPDATE banners
            SET title = %s,
                image_url = %s,
                priority = %s,
                active = %s
            WHERE id = %s
            RETURNING id, title, image_url, priority, active
        """, (title, image_url, priority, active, banner_id))
        row = cur.fetchone()
        if not row:
            return None, "Banner not found"
        return row, None

async def delete_banner(banner_id: UUID):
    with db_cursor(dict_cursor=True) as cur:
        cur.execute("DELETE FROM banners WHERE id=%s RETURNING id", (banner_id,))
        return None if cur.fetchone() else "Banner not found"