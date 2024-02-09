from pydantic import BaseModel, model_validator

from src.utils.enum_classes import CategoryGroup, BankKindGroup


class CategoryAdd(BaseModel):
    name: str
    icon: str | None = None


class ExpenseIncomeAdd(CategoryAdd):
    ...


class BankAdd(CategoryAdd):
    bank_group: BankKindGroup
    amount: float
    credit_card_limit: float | None = None
    credit_card_balance: float | None = None

    @model_validator(mode='after')
    def check_bank_group(self):
        if self.bank_group == BankKindGroup.credit_card:
            if self.credit_card_limit is None:
                raise ValueError('missing required field - credit_card_limit')
            if self.credit_card_balance is None:
                raise ValueError('missing required field - credit_card_balance')

        else:
            if self.credit_card_limit is not None:
                raise ValueError(
                    f'when bank is {self.bank_group.value}, credit card limit '
                    f'must be null')
            if self.credit_card_balance is not None:
                raise ValueError(
                    f'when bank is {self.bank_group.value}, credit card balance'
                    f' must be null')
        return self


class CategoryRead(BaseModel):
    id: int
    group: CategoryGroup
    position: int


class ExpenseIncomeRead(CategoryRead, ExpenseIncomeAdd):
    ...


class BankRead(CategoryRead, BankAdd):
    ...


class CategoryUpdate(BaseModel):
    name: str | None = None
    position: int | None = None
    icon: str | None = None
    amount: float | int | None = None
    credit_card_limit: float | None = None
    bank_balance: float | None = None
