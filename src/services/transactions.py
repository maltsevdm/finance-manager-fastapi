import datetime

from src.schemas.transactions import TransactionAdd, TransactionUpdate, \
    TransactionRead
from src.utils.enum_classes import CategoryGroup, TransactionGroup
from src.utils.unit_of_work import IUnitOfWork


class TransactionsService:
    async def add_one(
            self,
            uow: IUnitOfWork,
            user_id: int,
            transaction: TransactionAdd,
    ):
        async with uow:
            transaction_group, _, _ = await self._update_categories_amount(
                uow, transaction.id_category_from, transaction.id_category_to,
                action='add', amount=transaction.amount, user_id=user_id
            )

            transaction_dict = transaction.model_dump()
            transaction_dict['group'] = transaction_group
            transaction_dict['user_id'] = user_id

            db_transaction = await uow.transactions.add_one(transaction_dict)

            await uow.commit()

            return db_transaction

    async def remove_one(self, uow: IUnitOfWork, id: int, user_id: int):
        async with uow:
            db_transaction = await uow.transactions.drop_one(id=id,
                                                             user_id=user_id)

            await self._update_categories_amount(
                uow, db_transaction.id_category_from,
                db_transaction.id_category_to, action='remove',
                amount=db_transaction.amount,
                user_id=user_id
            )

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
            db_transaction_old = await uow.transactions.find_one(
                id=transaction_id, user_id=user_id)

            transaction_dict = transaction.model_dump()
            transaction_dict['group'] = db_transaction_old.group

            if (db_transaction_old.amount != transaction.amount
                    or db_transaction_old.id_category_from != transaction.id_category_from
                    or db_transaction_old.id_category_to != transaction.id_category_to):
                await self._update_categories_amount(
                    uow, db_transaction_old.id_category_from,
                    db_transaction_old.id_category_to, 'remove',
                    db_transaction_old.amount,
                    user_id=user_id
                )

                transaction_group, _, _ = await self._update_categories_amount(
                    uow, transaction.id_category_from,
                    transaction.id_category_to, 'add',
                    transaction.amount,
                    user_id=user_id
                )

                transaction_dict['group'] = transaction_group

            db_transaction = await uow.transactions.edit_one(
                db_transaction_old.id, **transaction_dict
            )

            await uow.commit()
            return db_transaction.to_read_model()

    async def _update_categories_amount(
            self, uow: IUnitOfWork, id_category_from: int, id_category_to: int,
            action: str, amount: float, user_id: int
    ) -> tuple[TransactionGroup, float, float]:
        '''
        :param action: add, remove
        :return: группа транзакции (transfer, expense, income), сумма категории from, сумма категории to.

        Если action == 'add', то из категории from вычитается
        new_amount, а в категорию to прибавляется.

        Если action == 'remove', то категорию from прибавляется
        old_amount, а в из категории to вычитается old_amount.
        '''
        db_category_from = await uow.categories.find_one(
            id=id_category_from, user_id=user_id)
        db_category_to = await uow.categories.find_one(
            id=id_category_to, user_id=user_id)

        transaction_group = self._get_transaction_group(db_category_from.group,
                                                        db_category_to.group)

        if action in 'add':
            if db_category_from.group == CategoryGroup.bank:
                db_category_from.amount -= amount

            if db_category_to.group == CategoryGroup.bank:
                db_category_to.amount += amount

        if action in 'remove':
            if db_category_from.group == CategoryGroup.bank:
                db_category_from.amount += amount

            if db_category_to.group == CategoryGroup.bank:
                db_category_to.amount -= amount

        return transaction_group, db_category_from.amount, db_category_to.amount

    def _get_transaction_group(
            self, group_from: CategoryGroup, group_to: CategoryGroup
    ):
        if (group_from == CategoryGroup.bank
                and group_to == CategoryGroup.bank):
            return TransactionGroup.transfer
        elif (group_from == CategoryGroup.bank
              and group_to == CategoryGroup.expense):
            return TransactionGroup.expense
        elif (group_from == CategoryGroup.income
              and group_to == CategoryGroup.bank):
            return TransactionGroup.income
        else:
            raise ValueError('The wrong direction of the transaction')

    async def get_all(self, uow: IUnitOfWork, **filters):
        async with uow:
            transactions = await uow.transactions.find_all_between_dates(
                **filters)

            return [TransactionRead.model_validate(x, from_attributes=True)
                    for x in transactions]
