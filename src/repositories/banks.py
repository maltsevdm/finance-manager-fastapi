from src.db.models import Bank
from src.repositories.categories import CategoriesRepository


class BanksRepository(CategoriesRepository):
    model = Bank
    position_criteria = ['user_id']
