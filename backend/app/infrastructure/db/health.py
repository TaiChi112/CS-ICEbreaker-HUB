from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.infrastructure.db.session import get_engine


async def check_database_connection() -> bool:
    try:
        engine = get_engine()
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return True
    except (SQLAlchemyError, ModuleNotFoundError):
        return False
