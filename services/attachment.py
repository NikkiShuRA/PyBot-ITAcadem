from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db_class.models import Attachment


async def list_attachment(db: AsyncSession) -> str:
    result = await db.execute(select(Attachment))
    users = result.scalars().all()

    if not users:
        return "Пользователей пока нет."

    lines = []
    for u in users:
        parts = [u.first_name or "", u.last_name or "", u.patronymic or ""]
        full_name = " ".join(p for p in parts if p).strip()
        lines.append(f"{u.id}: {full_name or '—'} (tg_id={u.telegram_id})")

    return "Список пользователей:\n" + "\n".join(lines)
