import logging

import uvicorn
from fastapi import FastAPI
from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..core.config import settings
from .view import UserAdmin


def run_admin() -> None:
    logger = logging.getLogger(__name__)

    # Инициализация БД
    database_url = settings.database_url
    engine = create_async_engine(
        database_url,
        echo=True,  # для отладки
        connect_args={"check_same_thread": False},
    )
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    # SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # FastAPI приложение
    admin_app = FastAPI(title="ITAcadem Admin Panel")

    # Регистрация админ-панели
    admin = Admin(
        app=admin_app,
        engine=engine,
        session_maker=session_maker,  # ← это ключевой момент!
        title="🎓 ITAcadem Admin",
        logo_url="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png",
    )

    # Регистрация ModelView (классы)
    admin.add_view(UserAdmin)
    # admin.add_view(LevelAdmin)
    # admin.add_view(TaskAdmin)
    # и т.д.
    logger.info("🔧 Starting Admin Panel on http://localhost:8001/admin")
    uvicorn.run(admin_app, host="127.0.0.1", port=8001)


# if __name__ == "__main__":
#     import uvicorn
