import enum


class CategoryGroup(enum.Enum):
    income = "income"
    expense = "expense"
    bank = "bank"


class TransactionGroup(enum.Enum):
    income = 'income'
    expense = 'expense'
    transfer = 'transfer'
