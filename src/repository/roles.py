import contextlib
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import HTTPException, status
from libgravatar import Gravatar
from sqlalchemy import select, func, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, Role
from src.schemas.roles import RoleEnum
from src.schemas.users import UserModel


class RoleABC(ABC):

    @abstractmethod
    async def get_role_by_name(self, name: str) -> Optional[User]:
        pass


class RoleDB(RoleABC):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        pass

    async def get_role_by_name(self, rolename: RoleEnum) -> Optional[User]:
        query = select(Role).where(Role.name == rolename)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()
