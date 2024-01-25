from src.db.models import CategoryAmount
from src.utils.repository import SQLAlchemyRepository


class CategoriesAmountRepository(SQLAlchemyRepository):
    model = CategoryAmount

    async def find_one(self, **filters) -> CategoryAmount:
        await super().find_one(**filters)

    async def find_all(self, order_by=None, **filters) -> list[CategoryAmount]:
        await super().find_all(order_by=order_by, **filters)
