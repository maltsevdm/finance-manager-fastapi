from abc import ABC, abstractmethod

from src.db.database import async_session
from src.repositories.categories import CategoriesRepository
from src.repositories.transations import TransactionsRepository


class IUnitOfWork(ABC):
    categories: CategoriesRepository
    transactions: TransactionsRepository

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, *args):
        pass

    @abstractmethod
    async def commit(self):
        pass

    @abstractmethod
    async def rollback(self):
        pass


class UnitOfWork:
    def __init__(self):
        self.session_factory = async_session

    async def __aenter__(self):
        self.session = self.session_factory()

        self.categories = CategoriesRepository(self.session)
        self.transactions = TransactionsRepository(self.session)

    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
