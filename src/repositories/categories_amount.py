from src.db.models import CategoryAmount
from src.utils.repository import SQLAlchemyRepository


class CategoriesAmountRepository(SQLAlchemyRepository):
    model = CategoryAmount
