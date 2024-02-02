import pytest
from httpx import AsyncClient
from sqlalchemy import select, delete

from src.db.database import async_session
from src.db.models import Category
from src.repositories.categories import CategoriesRepository


class TestCategories:
    async def check_order(self, group):
        async with async_session() as db:
            query = select(Category).filter_by(group=group)
            categories = (await db.execute(query)).scalars().all()
            i = 1
            for category in sorted(categories, key=lambda x: x.position):
                assert category.position == i
                i += 1

    @pytest.mark.parametrize(
        'name, group, position, status_code',
        [
            ('products', 'expense', '', 1, 200),  # id = 1
            ('transport', 'expense', 2, 200),  # id = 2
            ('other', 'expense', 3, 200),  # id = 3
            ('tinkoff black', 'bank', 1, 200),  # id = 4
            ('tinkoff s7', 'bank', 2, 200),  # id = 5
            ('alpha', 'bank', 3, 200),  # id = 6
            ('parents', 'income', 1, 200),  # id = 7
            ('salary', 'income', 2, 200),  # id = 8
            ('salary', 'incom', 3, 422),  # Неправильное имя группы
            ('salary', 'income', 3, 400),  # Повторяющееся имя категории
        ]
    )
    async def test_add_category(
            self, ac: AsyncClient, token, name, group, position, status_code
    ):
        response = await ac.post(
            '/api/categories',
            json=
            {
                'name': name,
                'group': group,
                # 'icon': 'string'
            },
            cookies={'value': token}
        )
        category = response.json()
        assert response.status_code == status_code
        if status_code == 200:
            assert category['position'] == position

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
    async def test_get_categories(
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
            (8, 200),
            (9, 400),  # Несуществующий индекс
        ]
    )
    async def test_remove_category(
            self, ac: AsyncClient, token, id, status_code
    ):
        response = await ac.delete(
            f'/api/categories/{id}',
            cookies={'value': token}
        )

        assert response.status_code == status_code
        if status_code != 200:
            return

        await self.check_order(response.json()['group'])

    @pytest.mark.parametrize(
        'id, data, status_code',
        [
            (4, {'amount': 5000}, 200),
            (4, {'position': 2}, 200),
            (4, {'name': 'no products'}, 200),
            (4, {'icon': 'new icon'}, 200),
            (4, {'position': 1}, 200),
        ]
    )
    async def test_update_category(
            self, ac: AsyncClient, token, id, data, status_code
    ):
        response = await ac.patch(
            f'/api/categories/{id}',
            json=data,
            cookies={'value': token}
        )
        assert response.status_code == status_code
        if status_code != 200:
            return

        category = response.json()
        if 'amount' in data:
            assert category['amount'] == data['amount']

        await self.check_order(category['group'])

        if 'name' in data:
            assert category['name'] == data['name']

        if 'icon' in data:
            assert category['icon'] == data['icon']

    async def truncate_table(self, session, model):
        stmt = delete(model)
        await session.execute(stmt)

    async def test_get_category_by_id(self, ac: AsyncClient, token):
        async with async_session() as session:
            await self.truncate_table(session, Category)

            data = {
                'user_id': 1,
                'group': 'income',
                'name': 'salary',
                'icon': 'string',
                'position': 1
            }

            category = await CategoriesRepository(session).add_one(data)

            response = await ac.get(
                f'/api/categories/{category.id}',
                cookies={'value': token}
            )
            print(response.json())


