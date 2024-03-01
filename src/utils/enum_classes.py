import enum


class ExpenseIncomeGroup(enum.Enum):
    income = 'income'
    expense = 'expense'


class BankGroup(enum.Enum):
    bank = 'bank'


class BankKindGroup(enum.Enum):
    cash = 'cash'
    debit_card = 'debit_card'
    credit_card = 'credit_card'


class CategoryGroup(enum.Enum):
    income = 'income'
    expense = 'expense'
    bank = 'bank'


class TransactionGroup(enum.Enum):
    income = 'income'
    expense = 'expense'
    transfer = 'transfer'


class TransactionStatus(enum.Enum):
    fact = 'fact'
    predict = 'predict'


if __name__ == '__main__':
    print(CategoryGroup.income)
