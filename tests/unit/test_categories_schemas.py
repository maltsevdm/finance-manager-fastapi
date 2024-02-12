import pytest
from pydantic import ValidationError

from src.schemas.categories import ExpenseIncomeAdd, BankAdd
from src.utils.enum_classes import CategoryGroup, BankKindGroup


@pytest.mark.parametrize(
    'group, bank_group, amount, credit_card_limit, card_balance, status',
    [
        (CategoryGroup.expense, None, None, None, None, 'ok'),
        (CategoryGroup.expense, BankKindGroup.credit_card, None, None, None,
         'ValidationError'),
        (CategoryGroup.expense, BankKindGroup.credit_card, 100, 200, 300,
         'ValidationError'),
        (CategoryGroup.expense, None, None, 300, None, 'ValidationError'),
        (CategoryGroup.bank, None, None, None, None, 'ValidationError'),
        (CategoryGroup.bank, BankKindGroup.cash, None, None, None,
         'ValidationError'),
    ]
)
def test_category_schema_add(
        group, credit_card_limit, card_balance, amount, bank_group, status
):
    er = 'ok'
    try:
        ExpenseIncomeAdd(
            name='test',
            group=group,
            credit_card_limit=credit_card_limit,
            card_balance=card_balance,
            amount=amount,
            bank_group=bank_group
        )
    except ValidationError:
        er = 'ValidationError'
    assert status == er


@pytest.mark.parametrize(
    'bank_group, amount, credit_card_limit, credit_card_balance, status',
    [
        (BankKindGroup.cash, 100, None, None, 'ok'),
        (BankKindGroup.cash, None, None, None, 'ValidationError'),
        (BankKindGroup.cash, 100, 100, None, 'ValidationError'),
        (BankKindGroup.cash, 100, 100, 100, 'ValidationError'),
        (BankKindGroup.cash, 100, None, 100, 'ValidationError'),
        (BankKindGroup.debit_card, 100, None, None, 'ok'),
        (BankKindGroup.debit_card, None, None, None, 'ValidationError'),
        (BankKindGroup.debit_card, 100, 100, None, 'ValidationError'),
        (BankKindGroup.debit_card, 100, 100, 100, 'ValidationError'),
        (BankKindGroup.debit_card, 100, None, 100, 'ValidationError'),
        (BankKindGroup.credit_card, 100, 100, 100, 'ok'),
        (BankKindGroup.credit_card, None, None, None, 'ValidationError'),
        (BankKindGroup.credit_card, 100, None, None, 'ValidationError'),
        (BankKindGroup.credit_card, 100, 100, None, 'ValidationError'),
        (BankKindGroup.credit_card, 100, None, 100, 'ValidationError'),
        (BankKindGroup.credit_card, None, None, 100, 'ValidationError'),
    ]
)
def test_bank_add_schema(
        bank_group, amount, credit_card_limit, credit_card_balance, status
):
    er = 'ok'
    try:
        BankAdd(
            name='test',
            bank_group=bank_group,
            amount=amount,
            credit_card_limit=credit_card_limit,
            credit_card_balance=credit_card_balance
        )
    except ValidationError:
        er = 'ValidationError'
    assert status == er
