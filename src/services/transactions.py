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
            db_category_from = await uow.categories.find_one(
                id=transaction.id_category_from)
            db_category_from.amount -= transaction.amount

            db_category_to = await uow.categories.find_one(
                id=transaction.id_category_to)
            db_category_to.amount += transaction.amount

            transaction_dict = transaction.model_dump()
            db_transaction = await uow.transactions.add_one(
                user_id, transaction_dict)

            await uow.commit()

            new_balance = await uow.categories.calc_sum(
                user_id=user_id, group=CategoryGroup.bank
            )

            expenses = await uow.transactions.calc_sum(
                date_from=get_start_month_date(),
                user_id=user_id, group=TransactionGroup.expense
            )

            incomes = await uow.transactions.calc_sum(
                date_from=get_start_month_date(),
                user_id=user_id, group=TransactionGroup.income
            )

            return {
                'new_balance': new_balance,
                'amount_category_from': db_category_from.amount,
                'amount_category_to': db_category_to.amount,
                'expenses': expenses if expenses else 0,
                'incomes': incomes if incomes else 0,
                'transaction': db_transaction.to_read_model()
            }

    async def remove_one(self, uow: IUnitOfWork, id: int):
        async with uow:
            db_transaction = await uow.transactions.drop_one(id=id)
            user_id = db_transaction.user_id

            db_category_from = await uow.categories_amount.find_one(
                id=db_transaction.id_category_from)
            db_category_from.amount += db_transaction.amount

            db_category_to = await uow.categories_amount.find_one(
                id=db_transaction.id_category_to)
            db_category_to.amount -= db_transaction.amount

            await uow.commit()

            new_balance = await uow.categories.calc_sum(
                user_id=user_id, group=CategoryGroup.bank
            )

            expenses = await uow.transactions.calc_sum(
                date_from=get_start_month_date(),
                user_id=user_id, group=TransactionGroup.expense
            )

            incomes = await uow.transactions.calc_sum(
                date_from=get_start_month_date(),
                user_id=user_id, group=TransactionGroup.income
            )

            return {
                'new_balance': new_balance,
                'amount_category_from': db_category_from.amount,
                'amount_category_to': db_category_to.amount,
                'expenses': expenses if expenses else 0,
                'incomes': incomes if incomes else 0,
                'transaction': db_transaction.to_read_model()
            }








