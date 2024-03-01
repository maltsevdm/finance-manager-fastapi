from src.db.database import async_session
from src.repositories.banks import BanksRepository
from src.schemas.categories import BankRead
from src.services.categories import CategoriesService
from src.services.transactions import TransactionsService
from src.utils.enum_classes import BankKindGroup
from src.utils.unit_of_work import IUnitOfWork


class BanksService(CategoriesService):
    repository = BanksRepository
    schema_read = BankRead

    async def get_all(
            self,
            uow: IUnitOfWork,
            user_id: int,
            id: int | None = None,
            group: BankKindGroup | None = None
    ):
        async with uow:
            await TransactionsService().check_predict_transactions(uow, user_id)

        async with async_session() as session:
            filters = {'user_id': user_id}
            if id is not None:
                filters['id'] = id
            if group is not None:
                filters['group'] = group

            categories = await self.repository(session).find_all(**filters)

            return [
                self.schema_read.model_validate(category, from_attributes=True)
                for category in categories]
