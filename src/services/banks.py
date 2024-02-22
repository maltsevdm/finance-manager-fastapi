from src.repositories.banks import BanksRepository
from src.schemas.categories import BankRead
from src.services.categories import CategoriesService


class BanksService(CategoriesService):
    repository = BanksRepository
    schema_read = BankRead
