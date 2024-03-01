from pydantic import BaseModel, model_validator

from src.utils.enum_classes import BankKindGroup, ExpenseIncomeGroup


class CategoryAdd(BaseModel):
    name: str
    icon: str | None = None


class ExpenseIncomeAdd(CategoryAdd):
    group: ExpenseIncomeGroup
    monthly_limit: float | None = None


class BankAdd(CategoryAdd):
    group: BankKindGroup
    amount: float
    credit_card_limit: float | None = None
    credit_card_balance: float | None = None

    @model_validator(mode='after')
    def check_bank_group(self):
        attrs_to_check = ['credit_card_limit', 'credit_card_balance']

        if self.group == BankKindGroup.credit_card:
            for attr in attrs_to_check:
                if getattr(self, attr) is None:
                    raise ValueError(f'missing required field - {attr}')
        else:
            for attr in attrs_to_check:
                if getattr(self, attr) is not None:
                    raise ValueError(f'when bank is {self.group.value}, '
                                     f'{attr} must be null')
        return self


class CategoryRead(BaseModel):
    id: int
    position: int


class ExpenseIncomeRead(CategoryRead, ExpenseIncomeAdd):
    amount: float


class BankRead(CategoryRead, BankAdd):
    ...


class CategoryUpdate(BaseModel):
    name: str | None = None
    position: int | None = None
    icon: str | None = None


class BankUpdate(CategoryUpdate):
    amount: float | None = None
    credit_card_limit: float | None = None
    credit_card_balance: float | None = None
    monthly_limit: float | None = None


class EiCategoryUpdate(CategoryUpdate):
    monthly_limit: float | None = None


class CategoriesFilters(BaseModel):
    id: int | None = None


class BanksFilters(CategoriesFilters):
    group: BankKindGroup | None = None


class EiCategoriesFilters(CategoriesFilters):
    group: ExpenseIncomeGroup | None = None
