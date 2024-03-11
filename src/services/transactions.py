import asyncio
import datetime

import aioschedule
from sqlalchemy import select, desc
from sqlalchemy.orm import aliased

from src.db.models import Bank, ExpenseIncomeCategory

from src.schemas.transactions import (
    TransactionAdd, TransactionUpdate, TransactionPrettyRead)
from src.utils.enum_classes import (
    TransactionGroup, ExpenseIncomeGroup, BankKindGroup, TransactionStatus)
from src.utils.unit_of_work import IUnitOfWork, UnitOfWork


class TransactionsService:
    async def _get_bank_and_dest(
            self, uow, group: TransactionGroup, bank_id: int, dest_id: int,
            user_id: int
    ) -> tuple[Bank, Bank | ExpenseIncomeCategory]:
        db_bank = await uow.banks.find_one(id=bank_id, user_id=user_id)

        if group == TransactionGroup.transfer:
            db_destination = await uow.banks.find_one(
                id=dest_id, user_id=user_id)
        else:
            db_destination = await uow.ei_categories.find_one(
                id=dest_id, user_id=user_id)

        return db_bank, db_destination

    async def _check_predict_transactions(self):
        uow = UnitOfWork()
        async with uow:
            transactions = await uow.transactions.update_predict_transactions()

            for transaction in transactions:
                db_bank, db_dest = await self._get_bank_and_dest(
                    uow, transaction.group, transaction.bank_id,
                    transaction.destination_id, transaction.user_id)

                match transaction.group:
                    case TransactionGroup.transfer:
                        db_bank.decrease_amount(transaction.amount)
                        db_dest.increase_amount(transaction.amount)
                    case TransactionGroup.expense:
                        db_bank.decrease_amount(transaction.amount)
                    case TransactionGroup.income:
                        db_bank.increase_amount(transaction.amount)

                transaction.status = TransactionStatus.was_predict

            await uow.commit()
            print(f'Transactions updated. Count: {len(transactions)}')

    async def add_one(
            self,
            uow: IUnitOfWork,
            user_id: int,
            transaction: TransactionAdd,
    ):
        async with uow:
            db_bank, db_dest = await self._get_bank_and_dest(
                uow, transaction.group, transaction.bank_id,
                transaction.destination_id, user_id)

            if (transaction.group == TransactionGroup.expense
                    and db_dest.group != ExpenseIncomeGroup.expense):
                raise ValueError('Неверное направление транзакции.')

            if (transaction.group == TransactionGroup.income
                    and db_dest.group != ExpenseIncomeGroup.income):
                raise ValueError('Неверное направление транзакции.')

            if (transaction.group == TransactionGroup.transfer
                    and not isinstance(db_dest.group, BankKindGroup)):
                raise ValueError('Неверное направление транзакции.')

            transaction_dict = transaction.model_dump()
            transaction_dict['user_id'] = user_id
            transaction_dict['status'] = TransactionStatus.predict

            if transaction.date <= datetime.date.today():
                transaction_dict['status'] = TransactionStatus.fact
                match transaction.group:
                    case TransactionGroup.transfer:
                        db_bank.decrease_amount(transaction.amount)
                        db_dest.increase_amount(transaction.amount)
                    case TransactionGroup.expense:
                        db_bank.decrease_amount(transaction.amount)
                    case TransactionGroup.income:
                        db_bank.increase_amount(transaction.amount)

            db_transaction = await uow.transactions.add_one(transaction_dict)
            await uow.commit()

            return db_transaction

    async def remove_one(self, uow: IUnitOfWork, id: int, user_id: int):
        async with uow:
            db_transaction = await uow.transactions.drop_one(id=id,
                                                             user_id=user_id)

            if db_transaction.status != TransactionStatus.predict:
                db_bank, db_dest = await self._get_bank_and_dest(
                    uow, db_transaction.group, db_transaction.bank_id,
                    db_transaction.destination_id, user_id)

                match db_transaction.group:
                    case TransactionGroup.transfer:
                        db_bank.increase_amount(db_transaction.amount)
                        db_dest.decrease_amount(db_transaction.amount)
                    case TransactionGroup.expense:
                        db_bank.increase_amount(db_transaction.amount)
                    case TransactionGroup.income:
                        db_bank.decrease_amount(db_transaction.amount)

            await uow.commit()
            return db_transaction

    async def update_one(
            self,
            uow: IUnitOfWork,
            transaction_id: int,
            transaction: TransactionUpdate,
            user_id: int
    ):
        async with uow:
            old_transaction_db = await self.remove_one(
                uow, transaction_id, user_id=user_id)

            old_transaction = TransactionAdd.model_validate(old_transaction_db,
                                                            from_attributes=True)
            transaction_dict = transaction.model_dump()
            for attr, value in transaction_dict.items():
                if value is not None:
                    setattr(old_transaction, attr, value)
            db_transaction = await self.add_one(uow, user_id, old_transaction)

            return db_transaction

            # db_transaction = await uow.transactions.find_one(
            #     id=transaction_id, user_id=user_id)
            #
            # transaction_dict = transaction.model_dump()
            #
            # is_amount_changed = (transaction.amount is not None
            #                      and db_transaction.amount != transaction.amount)
            # is_bank_changed = (transaction.bank_id is not None
            #                    and db_transaction.bank_id != transaction.bank_id)
            # is_dest_changed = (transaction.destination_id is not None
            #                    and db_transaction.destination_id != transaction.destination_id)
            #
            # if is_amount_changed or is_bank_changed:
            #     # Если поменялось либо сумма, либо счет списания
            #
            #     db_bank_old: Bank = await uow.banks.find_one(
            #         id=db_transaction.bank_id, user_id=user_id)
            #     if db_transaction.bank_id != transaction.bank_id:
            #         db_bank_new: Bank = await uow.banks.find_one(
            #             id=transaction.bank_id, user_id=user_id)
            #     else:
            #         db_bank_new: Bank = db_bank_old
            #
            #     db_bank_old.increase_amount(db_transaction.amount)
            #     db_bank_new.decrease_amount(transaction.amount)
            #
            # if ((is_dest_changed or is_amount_changed)
            #         and db_transaction.group == TransactionGroup.transfer):
            #     # Если поменялось либо сумма, либо счет назначения,
            #     # и если это перевод
            #
            #     db_dest_old: Bank = await uow.banks.find_one(
            #         id=db_transaction.destination_id, user_id=user_id)
            #
            #     if db_transaction.destination_id != transaction.destination_id:
            #         db_dest_new: Bank = await uow.banks.find_one(
            #             id=transaction.destination_id, user_id=user_id)
            #     else:
            #         db_dest_new: Bank = db_dest_old
            #
            #     db_dest_old.decrease_amount(db_transaction.amount)
            #     db_dest_new.increase_amount(transaction.amount)
            #
            # transaction_dict = {k: v for k, v in transaction_dict.items() if v is not None}
            #
            # db_transaction = await uow.transactions.edit_one(
            #     id=db_transaction.id, data=transaction_dict
            # )
            #
            # await uow.commit()
            # return TransactionRead.model_validate(db_transaction,
            #                                       from_attributes=True)

    async def calc_sum(
            self, uow: IUnitOfWork, user_id: int, **filters
    ) -> float:
        async with uow:
            return await uow.transactions.calc_sum(user_id=user_id, **filters)

    async def get_all(
            self, uow: IUnitOfWork,
            user_id: int,
            limit: int | None = None,
            offset: int | None = None,
            group: TransactionGroup | None = None,
            date_from: datetime.date | None = None,
            date_to: datetime.date | None = None,
            **filters
    ):
        async with uow:
            t = aliased(uow.transactions.model)
            b = aliased(uow.banks.model)
            eic = aliased(uow.ei_categories.model)

            cte = select(b.id, b.name).union_all(select(eic.id, eic.name)).cte()
            cte2 = aliased(cte)

            query = (
                select(
                    t.id,
                    t.group,
                    cte.c.name.label('bank_name'),
                    cte2.c.name.label('destination_name'),
                    t.amount,
                    t.date,
                    t.note
                )
                .join(cte, t.bank_id == cte.c.id)
                .join(cte2, t.destination_id == cte2.c.id)
                .filter(t.user_id == user_id)
            )

            if date_from:
                query = query.filter(t.date >= date_from)
            if date_to:
                query = query.filter(t.date <= date_to)
            if group:
                query = query.filter(t.group == group)

            query = query.order_by(desc(t.date))

            if offset is not None:
                query = query.offset(offset)
            if limit is not None:
                query = query.limit(limit)

            res = await uow.session.execute(query)
            transactions = res.all()

            return [
                TransactionPrettyRead.model_validate(x, from_attributes=True)
                for x in transactions]

    async def observe_transactions(self):
        aioschedule.every().day.at('00:00').do(self._check_predict_transactions)

        while True:
            await aioschedule.run_pending()
            await asyncio.sleep(0)
