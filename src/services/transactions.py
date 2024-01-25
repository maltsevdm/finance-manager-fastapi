from src.schemas.transactions import TransactionCreate
from src.utils.unit_of_work import IUnitOfWork
from src.utils.utils import get_start_month_date


class TransactionsService:
    async def add_one(
            self,
            uow: IUnitOfWork,
            user_id: int,
            transaction: TransactionCreate,
    ):
        async with uow:
            db_category_amount_from = await uow.categories_amount.find_one(
                category_id=transaction.id_category_from,
                date=get_start_month_date()
            )
            db_category_amount_from.amount -= transaction.amount

            db_category_amount_to = await uow.categories_amount.find_one(
                category_id=transaction.id_category_to,
                date=get_start_month_date()
            )
            db_category_amount_to.amount += transaction.amount

            transaction_dict = transaction.model_dump()
            await uow.transactions.add_one(user_id, transaction_dict)







