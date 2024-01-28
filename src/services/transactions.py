from src.schemas.transactions import TransactionCreate
from src.utils.enum_classes import CategoryGroup, TransactionGroup
from src.utils.unit_of_work import IUnitOfWork
from src.utils.utils import get_start_month_date


# SELECT category.id, category.name, SUM(transaction.amount) AS amount
# FROM category
# JOIN transaction ON category.id = transaction.id_category_to
# WHERE category."group" = 'expense'
# GROUP BY category.id;

class TransactionsService:
    async def add_one(
            self,
            uow: IUnitOfWork,
            user_id: int,
            transaction: TransactionCreate,
    ):
        async with uow:
            transaction_group, _, _ = await self.update_categories_amount(
                uow, transaction.id_category_from, transaction.id_category_to,
                action='add', amount=transaction.amount
            )

            transaction_dict = transaction.model_dump()
            transaction_dict['group'] = transaction_group

            db_transaction = await uow.transactions.add_one(
                user_id, transaction_dict)

            await uow.commit()

            return db_transaction.to_read_model()

    async def remove_one(self, uow: IUnitOfWork, id: int, user_id: int):
        async with uow:
            db_transaction = await uow.transactions.drop_one(id=id)
            if user_id != db_transaction.user_id:
                raise PermissionError('Incorrect transaction id.')

            await self.update_categories_amount(
                uow, db_transaction.id_category_from,
                db_transaction.id_category_to, action='remove',
                amount=db_transaction.amount
            )

            await uow.commit()
            return db_transaction.to_read_model()

    async def update_one(
            self,
            uow: IUnitOfWork,
            transaction_id: int,
            transaction: TransactionCreate,
            user_id: int
    ):
        async with uow:
            db_transaction_old = await uow.transactions.find_one(
                id=transaction_id)

            transaction_dict = transaction.model_dump()
            transaction_dict['group'] = db_transaction_old.group

            if (db_transaction_old.amount != transaction.amount
                    or db_transaction_old.id_category_from != transaction.id_category_from
                    or db_transaction_old.id_category_to != transaction.id_category_to):
                await self.update_categories_amount(
                    uow, db_transaction_old.id_category_from,
                    db_transaction_old.id_category_to, 'remove',
                    db_transaction_old.amount
                )

                transaction_group, _, _ = await self.update_categories_amount(
                    uow, transaction.id_category_from,
                    transaction.id_category_to, 'add',
                    transaction.amount
                )

                transaction_dict['group'] = transaction_group

            db_transaction = await uow.transactions.edit_one(
                db_transaction_old.id, **transaction_dict
            )

            await uow.commit()
            return db_transaction.to_read_model()

    async def update_categories_amount(
            self, uow: IUnitOfWork, id_category_from: int, id_category_to: int,
            action: str, amount: float
    ) -> tuple[TransactionGroup, float, float]:
        '''
        :param action: add, remove
        :return: группа транзакции (transfer, expense, income), сумма категории from, сумма категории to.

        Если action == 'add', то из категории from вычитается
        new_amount, а в категорию to прибавляется.

        Если action == 'remove', то категорию from прибавляется
        old_amount, а в из категории to вычитается old_amount.
        '''
        db_category_from = await uow.categories.find_one(id=id_category_from)
        db_category_to = await uow.categories.find_one(id=id_category_to)

        transaction_group = self.get_transaction_group(db_category_from.group,
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

    def get_transaction_group(
            self, group_from: CategoryGroup, group_to: CategoryGroup
    ):
        '''

        :param group_from:
        :param group_to:
        :return:
        '''

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
