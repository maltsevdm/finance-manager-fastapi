from src.schemas.debts import DebtAdd, DebtRead, DebtUpdate
from src.utils.enum_classes import CategoryGroup
from src.utils.unit_of_work import IUnitOfWork


class DebtsService:
    async def add_one(
            self, uow: IUnitOfWork, user_id: int, debt: DebtAdd
    ):
        debt_dict = debt.model_dump()
        async with uow:
            debt_dict['user_id'] = user_id
            db_debt = await uow.debts.add_one(debt_dict)

            await self._update_categories_card_balance(
                uow, user_id,
                id_bank_new=debt.bank_id, amount_new=debt.amount
            )

            await uow.commit()
            return db_debt

    async def remove_one(
            self, uow: IUnitOfWork, user_id: int, id: int
    ):
        async with uow:
            db_debt = await uow.debts.drop_one(id=id, user_id=user_id)

            await self._update_categories_card_balance(
                uow, user_id,
                id_bank_old=db_debt.bank_id, amount_old=db_debt.amount
            )

            await uow.commit()
            return db_debt

    async def get_all(self, uow: IUnitOfWork, **filters):
        async with uow:
            debts = await uow.debts.find_all(**filters)
            return [DebtRead.model_validate(x, from_attributes=True)
                    for x in debts]

    async def _update_categories_card_balance(
            self, uow, user_id: int,
            id_bank_old: int | None = None,
            amount_old: float | None = None,
            id_bank_new: int | None = None,
            amount_new: float | None = None
    ):
        if id_bank_old is not None and amount_old is not None:
            db_bank_old = await uow.categories.find_one(
                id=id_bank_old, user_id=user_id,
                group=CategoryGroup.bank)
            db_bank_old.credit_card_balance += amount_old
            if id_bank_new is None and amount_new is not None:
                db_bank_old.credit_card_balance -= amount_new

        if id_bank_new is not None:
            db_bank_new = await uow.categories.find_one(
                id=id_bank_new, user_id=user_id,
                group=CategoryGroup.bank)

            db_bank_new.credit_card_balance -= amount_old if amount_new is None else amount_new

    async def update_one(
            self, uow: IUnitOfWork, id: int, user_id: int, debt: DebtUpdate
    ):
        debt_dict = debt.model_dump()
        async with uow:
            db_debt = await uow.debts.find_one(id=id, user_id=user_id)

            if debt.amount is not None and debt.bank_id is not None:
                # Если обновились счёт и сумма
                await self._update_categories_card_balance(
                    uow, id_bank_old=db_debt.bank_id,
                    id_bank_new=debt.bank_id, amount_old=db_debt.amount,
                    amount_new=debt.amount, user_id=user_id)

            elif debt.amount is not None:
                # Если обновилась только сумма
                await self._update_categories_card_balance(
                    uow, id_bank_old=db_debt.bank_id, amount_old=db_debt.amount,
                    amount_new=debt.amount, user_id=user_id)

            elif debt.bank_id is not None:
                # Если обновился только счёт
                await self._update_categories_card_balance(
                    uow, id_bank_old=db_debt.bank_id,
                    id_bank_new=debt.bank_id, amount_old=db_debt.amount,
                    user_id=user_id)

            for attr, value in debt_dict.items():
                if value is not None:
                    setattr(db_debt, attr, value)

            await uow.commit()
            return db_debt
