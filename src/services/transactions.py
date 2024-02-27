from src.db.models import Bank, ExpenseIncomeCategory
from src.schemas.transactions import (
    TransactionAdd, TransactionUpdate, TransactionRead)
from src.utils.enum_classes import TransactionGroup
from src.utils.unit_of_work import IUnitOfWork


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

            match transaction.group:
                case TransactionGroup.transfer:
                    db_bank.decrease_amount(transaction.amount)
                    db_dest.increase_amount(transaction.amount)
                case TransactionGroup.expense:
                    db_bank.decrease_amount(transaction.amount)
                case TransactionGroup.income:
                    db_bank.increase_amount(transaction.amount)

            transaction_dict = transaction.model_dump()
            transaction_dict['user_id'] = user_id

            db_transaction = await uow.transactions.add_one(transaction_dict)
            await uow.commit()

            return db_transaction

    async def remove_one(self, uow: IUnitOfWork, id: int, user_id: int):
        async with uow:
            db_transaction = await uow.transactions.drop_one(id=id,
                                                             user_id=user_id)

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
            db_transaction = await uow.transactions.find_one(
                id=transaction_id, user_id=user_id)

            transaction_dict = transaction.model_dump()

            if (db_transaction.amount != transaction.amount
                    or db_transaction.bank_id != transaction.bank_id):
                # Если поменялось либо сумма, либо счет списания

                db_bank_old = await uow.banks.find_one(
                    id=db_transaction.bank_id, user_id=user_id)
                if db_transaction.bank_id != transaction.bank_id:
                    db_bank_new = await uow.banks.find_one(
                        id=transaction.bank_id, user_id=user_id)
                else:
                    db_bank_new = db_bank_old

                db_bank_old.amount += db_transaction.amount
                db_bank_new.amount -= transaction.amount

            if ((db_transaction.destination_id != transaction.destination_id
                 or db_transaction.amount != transaction.amount)
                    and db_transaction.group == TransactionGroup.transfer):
                # Если поменялось либо сумма, либо счет назначения,
                # и если это перевод

                db_dest_old = await uow.banks.find_one(
                    id=db_transaction.destination_id, user_id=user_id)

                if db_transaction.destination_id != transaction.destination_id:
                    db_dest_new = await uow.banks.find_one(
                        id=transaction.destination_id, user_id=user_id)
                else:
                    db_dest_new = db_dest_old

                db_dest_old.amount -= db_transaction.amount
                db_dest_new.amount += transaction.amount

            db_transaction = await uow.transactions.edit_one(
                db_transaction.id, **transaction_dict
            )

            await uow.commit()
            return db_transaction.to_read_model()

    async def calc_sum(self, uow: IUnitOfWork, user_id: int,
                       **filters) -> float:
        async with uow:
            return await uow.transactions.calc_sum(user_id=user_id, **filters)

    async def get_all(self, uow: IUnitOfWork, **filters):
        async with uow:
            transactions = await uow.transactions.find_all_between_dates(
                **filters)

            return [TransactionRead.model_validate(x, from_attributes=True)
                    for x in transactions]
