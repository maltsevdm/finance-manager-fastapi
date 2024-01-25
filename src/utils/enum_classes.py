import enum


class CategoryGroup(enum.Enum):
    income = "income"
    expense = "expense"
    bank = "bank"


class OperationGroup(enum.Enum):
    income = 'income'
    expense = 'expense'
