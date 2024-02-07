from src.db.models import Debt
from src.utils.repository import SQLAlchemyRepository


class DebtsRepository(SQLAlchemyRepository):
    model = Debt
