import uuid
from typing import Any, Dict, List, Optional
from fastapi import HTTPException
from app.utils.database_async import fetch_one, fetch_all, execute
from ..models.message_model import ChatResponse, MessageResponse
from ..helpers.chat_message import _find_existing_chat, _ensure_participant


async def create_chat(sender_id: str, sender_type: str, receiver_id: str, receiver_type: str) -> ChatResponse:

    existing = await _find_existing_chat(sender_id, sender_type, receiver_id, receiver_type)
    if existing:
        return ChatResponse(
            chat_id=existing["id"],
            participants=[str(sender_id), str(receiver_id)],
            created_at=str(existing["created_at"])
        )

    new_chat = await fetch_one(
        """
        INSERT INTO chats (is_group)
        VALUES (FALSE)
        RETURNING id, created_at
        """
    )
    if not new_chat:
        raise HTTPException(status_code=500, detail="Chat oluşturulamadı")

    chat_id = str(new_chat["id"])

    await _ensure_participant(chat_id, sender_id, sender_type)
    await _ensure_participant(chat_id, receiver_id, receiver_type)

    return ChatResponse(
        chat_id=chat_id,
        participants=[str(sender_id), str(receiver_id)],
        created_at=str(new_chat["created_at"])
    )


async def send_message(
    chat_id: str,
    sender_id: str,
    sender_type: str,
    content: str
) -> MessageResponse:
    # 0) Chat exists and is 1-1 chat
    existing_chat = await fetch_one(
        """
        SELECT id, is_group
        FROM chats
        WHERE id = $1::uuid
        """,
        chat_id
    )
    if not existing_chat:
        raise HTTPException(status_code=404, detail="Sohbet bulunamadı")
    if existing_chat["is_group"]:
        raise HTTPException(status_code=400, detail="Grup sohbetinde tekil alıcı gereklidir")

    # 1) Sender belongs to this chat?
    sender_in = await fetch_one(
        """
        SELECT 1
        FROM chat_participants
        WHERE chat_id = $1::uuid
          AND user_id = $2::uuid
          AND user_type = $3
        LIMIT 1
        """,
        chat_id, sender_id, sender_type
    )
    if not sender_in:
        raise HTTPException(status_code=403, detail="Gönderen bu sohbetin katılımcısı değil")

    # 2) Infer receiver as 'the other participant'
    receiver = await fetch_one(
        """
        SELECT user_id, user_type
        FROM chat_participants
        WHERE chat_id = $1::uuid
          AND NOT (user_id = $2::uuid AND user_type = $3)
        LIMIT 1
        """,
        chat_id, sender_id, sender_type
    )
    if not receiver:
        raise HTTPException(status_code=400, detail="Alıcı bulunamadı (sohbette karşı taraf yok)")

    receiver_id = str(receiver["user_id"])
    receiver_type = receiver["user_type"]

    # 3) Insert into messages
    msg = await fetch_one(
        """
        INSERT INTO messages (sender_id, sender_type, receiver_id, receiver_type, content)
        VALUES ($1::uuid, $2, $3::uuid, $4, $5)
        RETURNING id, sender_type, content, sent_at, delivered_at, read_at
        """,
        sender_id, sender_type, receiver_id, receiver_type, content
    )
    if not msg:
        raise HTTPException(status_code=500, detail="Mesaj gönderilemedi")

    message_id = str(msg["id"])

    # 4) Relate it to chat
    await execute(
        """
        INSERT INTO chat_messages (chat_id, message_id)
        VALUES ($1::uuid, $2::uuid)
        ON CONFLICT (chat_id, message_id) DO NOTHING
        """,
        chat_id, message_id
    )

    # 5) Bump chat.updated_at
    await execute(
        "UPDATE chats SET updated_at = NOW() WHERE id = $1::uuid",
        chat_id
    )

    return MessageResponse(
        message_id=message_id,
        sender_type=msg["sender_type"],
        content=msg["content"],
        sent_at=str(msg["sent_at"]),
        delivered_at=str(msg["delivered_at"]) if msg["delivered_at"] else None,
        read_at=str(msg["read_at"]) if msg["read_at"] else None
    )


async def get_chats_for_user(user_id: str, user_type: str) -> List[Dict[str, Any]]:
    rows = await fetch_all(
        """
        SELECT
            c.id AS chat_id,
            c.created_at,
            c.updated_at,
            ARRAY_AGG(cp.user_id::text || ':' || cp.user_type ORDER BY cp.joined_at) AS participants
        FROM chats c
        JOIN chat_participants cp ON cp.chat_id = c.id
        WHERE c.id IN (
            SELECT chat_id FROM chat_participants
            WHERE user_id = $1::uuid AND user_type = $2
        )
        GROUP BY c.id
        ORDER BY c.updated_at DESC, c.created_at DESC
        """,
        user_id, user_type
    )

    return [
        {
            "chat_id": str(r["chat_id"]),
            "participants": list(r["participants"]),
            "created_at": str(r["created_at"]),
            "updated_at": str(r["updated_at"]),
        }
        for r in rows
    ]

async def get_chat_history(chat_id: str, user_id: str, user_type: str,
                           limit: int = 50,
                           ) -> List[Dict[str, Any]]:
    await fetch_one("""
        SELECT 1 FROM chat_participants
        WHERE chat_id = $1::uuid AND user_id = $2::uuid AND user_type = $3
        LIMIT 1
    """, chat_id, user_id, user_type) or HTTPException(403, "Bu sohbetin katılımcısı değilsin")

    base = """
      SELECT m.id, m.sender_id, m.sender_type, m.receiver_id, m.receiver_type,
             m.content, m.sent_at, m.delivered_at, m.read_at
      FROM chat_messages cm
      JOIN messages m ON m.id = cm.message_id
      WHERE cm.chat_id = $1::uuid
    """
    
    sql = base + " ORDER BY m.sent_at ASC LIMIT $2"
    args = (chat_id, limit,)

    rows = await fetch_all(sql, *args)
    return [{
        "message_id": str(r["id"]),
        "sender_id": str(r["sender_id"]),
        "sender_type": r["sender_type"],
        "receiver_id": str(r["receiver_id"]),
        "receiver_type": r["receiver_type"],
        "content": r["content"],
        "sent_at": str(r["sent_at"]),
        "delivered_at": str(r["delivered_at"]) if r["delivered_at"] else None,
        "read_at": str(r["read_at"]) if r["read_at"] else None,
    } for r in rows]

async def get_undelivered_messages(user_id: str, user_type: str) -> List[Dict[str, Any]]:
    """
    Bu kullanıcıya adreslenmiş ve delivered_at IS NULL olan mesajları
    TEK STATEMENT ile delivered_at = NOW() yapıp geri döndürür.
    """
    user_id = str(user_id)
    user_type_norm = user_type.lower()

    rows = await fetch_all(
        """
        WITH upd AS (
            UPDATE messages AS m
            SET delivered_at = NOW()
            WHERE m.receiver_id   = $1::uuid
              AND lower(m.receiver_type) = $2
              AND m.delivered_at IS NULL
            RETURNING
                m.id, m.sender_id, m.sender_type,
                m.receiver_id, m.receiver_type,
                m.content, m.sent_at, m.delivered_at, m.read_at
        )
        SELECT *
        FROM upd
        ORDER BY sent_at ASC
        """,
        user_id, user_type_norm
    )

    return [
        {
            "message_id": str(r["id"]),
            "sender_id": str(r["sender_id"]),
            "sender_type": r["sender_type"],
            "receiver_id": str(r["receiver_id"]),
            "receiver_type": r["receiver_type"],
            "content": r["content"],
            "sent_at": str(r["sent_at"]),
            "delivered_at": str(r["delivered_at"]) if r["delivered_at"] else None,
            "read_at": str(r["read_at"]) if r["read_at"] else None,
        }
        for r in rows
    ]

async def mark_messages_read(user_id: str, user_type: str, chat_id: str) -> Dict[str, Any]:
    # Güvenli tip normalizasyonu
    user_id  = str(user_id)
    chat_id  = str(chat_id)
    # Case-insensitive kıyas için küçült
    user_type_norm = user_type.lower()
    probe = await fetch_all(
        """
        SELECT m.id, m.receiver_id::text AS rid, m.receiver_type, m.read_at, m.sent_at
        FROM chat_messages cm
        JOIN messages m ON m.id = cm.message_id
        WHERE cm.chat_id = $1::uuid
        ORDER BY m.sent_at DESC
        LIMIT 10
        """,
        chat_id
    )
    print("READ_PROBE =>", probe)
    rows = await fetch_all(
        """
        UPDATE messages AS m
        SET read_at = NOW()
        FROM chat_messages AS cm
        WHERE
            cm.message_id = m.id
            AND cm.chat_id = $3::uuid
            AND m.receiver_id = $1::uuid
            AND lower(m.receiver_type) = $2
            AND m.read_at IS NULL
        RETURNING m.id
        """,
        user_id, user_type_norm, chat_id
    )
    print(rows)
    updated_ids = [str(r["id"]) for r in rows] if rows else []
    return {"updated_count": len(updated_ids), "message_ids": updated_ids}

