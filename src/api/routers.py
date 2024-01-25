from src.api.categories import router as router_categories
from src.api.transactions import router as router_transactions

all_routers = [
    router_categories,
    router_transactions
]
