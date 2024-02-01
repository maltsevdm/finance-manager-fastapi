import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.db.database import async_session
from src.db.models import Category


class __TestTransactions:
    @pytest.mark.parametrize(
        'id_from, id_to, amount, group, category_from_amount, category_to_amount, status_code',
        [
            (6, 3, 500, 'expense', -500, 0, 200),  # id = 1
            (7, 6, 600, 'income', 0, 100, 200),  # id = 2
            (4, 6, 700, 'transfer', -700, 800, 200),  # id = 3
            (5, 3, 500, 'expense', 0, 0, 400),  # Неверный id
            (4, 7, 500, 'expense', 0, 0, 400),  # Неправильное направление
            (4, 6, '100', 'transfer', -800, 900, 200),  # Сумма строкой, но в ней число
            (4, 6, 'aaa', 'transfer', -800, 900, 422),  # Сумма строкой, но в ней буквы
        ]
    )
    async def test_add_transaction(
            self, ac: AsyncClient, token, id_from, id_to, group, amount,
            status_code, category_from_amount, category_to_amount
    ):
        response = await ac.post(
            '/api/transactions',
            json=
            {
                'id_category_from': id_from,
                'id_category_to': id_to,
                'amount': amount,
            },
            cookies={'value': token}
        )

        assert response.status_code == status_code
        if status_code != 200:
            return
        transaction = response.json()
        assert transaction['group'] == group

        async with async_session() as db:
            category_from = await db.get(Category, id_from)
            category_to = await db.get(Category, id_to)

            assert category_from.amount == category_from_amount
            assert category_to.amount == category_to_amount

    @pytest.mark.parametrize(
        'group, count, status_code',
        [
            (None, 8, 200),
            ('income', 2, 200),
            ('expense', 3, 200),
            ('bank', 3, 200),
            ('incom', 0, 422),  # Неправильное имя группы
        ]
    )
    async def _test_get_categories(
            self, ac: AsyncClient, token, group, count, status_code
    ):
        if group:
            url = f'/api/categories/{group}'
        else:
            url = f'/api/categories'

        response = await ac.get(url, cookies={'value': token})
        categories = response.json()
        assert response.status_code == status_code
        if status_code == 200:
            assert len(categories) == count

    @pytest.mark.parametrize(
        'id, status_code',
        [
            (1, 200),
            (5, 200),
            (4, 200),
            (8, 200),
            (9, 400),  # Несуществующий индекс
        ]
    )
    async def _test_remove_category(
            self, ac: AsyncClient, token, id, status_code
    ):
        response = await ac.delete(
            f'/api/categories/?category_id={id}',
            cookies={'value': token}
        )

        assert response.status_code == status_code
        if status_code != 200:
            return

        async with async_session() as db:
            query = select(Category).filter_by(group=response.json()['group'])
            categories = (await db.execute(query)).scalars().all()
            i = 1
            for category in sorted(categories, key=lambda x: x.position):
                assert category.position == i
                i += 1
