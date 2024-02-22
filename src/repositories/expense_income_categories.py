from src.db.models import ExpenseIncomeCategory
from src.repositories.categories import CategoriesRepository


class ExpenseIncomeCategoriesRepository(CategoriesRepository):
    model = ExpenseIncomeCategory
    position_criteria = ['user_id', 'group']
