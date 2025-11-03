from typing import Optional, Dict, Any
from app.utils.database_async import fetch_one, execute

async def _find_existing_chat(sender_id: str, sender_type: str, receiver_id: str, receiver_type: str) -> Optional[Dict[str, Any]]:
    sql = """
    SELECT c.id, c.created_at
    FROM chats c
    JOIN chat_participants cp1
      ON cp1.chat_id = c.id AND cp1.user_id = $1::uuid AND cp1.user_type = $2
    JOIN chat_participants cp2
      ON cp2.chat_id = c.id AND cp2.user_id = $3::uuid AND cp2.user_type = $4
    WHERE c.is_group = FALSE
    LIMIT 1
    """
    return await fetch_one(sql, sender_id, sender_type, receiver_id, receiver_type)


async def _ensure_participant(chat_id: str, user_id: str, user_type: str) -> None:
    sql = """
    INSERT INTO chat_participants (chat_id, user_id, user_type)
    VALUES ($1::uuid, $2::uuid, $3)
    ON CONFLICT (chat_id, user_id, user_type) DO NOTHING
    """
    await execute(sql, chat_id, user_id, user_type)

