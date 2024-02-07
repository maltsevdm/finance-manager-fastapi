import enum


class CategoryGroup(enum.Enum):
    income = 'income'
    expense = 'expense'
    bank = 'bank'


class TransactionGroup(enum.Enum):
    income = 'income'
    expense = 'expense'
    transfer = 'transfer'


class BankGroup(enum.Enum):
    cash = 'cash'
    debit_card = 'debit_card'
    credit_card = 'credit_card'
