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
        attrs_to_check = ['credit_card_limit', 'credit_card_balance']

        if self.bank_group == BankKindGroup.credit_card:
            for attr in attrs_to_check:
                if getattr(self, attr) is None:
                    raise ValueError(f'missing required field - {attr}')
        else:
            for attr in attrs_to_check:
                if getattr(self, attr) is not None:
                    raise ValueError(f'when bank is {self.bank_group.value}, '
                                     f'{attr} must be null')
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


if __name__ == '__main__':
    BankAdd(name='cash', bank_group='cash', amount=0)
