from src.api.categories import router as router_categories
from src.api.transactions import router as router_transactions
from src.api.debts import router as router_debts
from src.api.icons import router as router_icons

all_routers = [
    router_categories,
    router_transactions,
    router_debts,
    router_icons
]
