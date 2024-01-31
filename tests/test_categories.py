import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.db.database import async_session
from src.db.models import Category


class TestCategories:
    @pytest.mark.parametrize(
        'name, group, position, status_code',
        [
            ('products', 'expense', 1, 200),
            ('transport', 'expense', 2, 200),
            ('other', 'expense', 3, 200),
            ('tinkoff black', 'bank', 1, 200),
            ('tinkoff s7', 'bank', 2, 200),
            ('alpha', 'bank', 3, 200),
            ('parents', 'income', 1, 200),
            ('salary', 'income', 2, 200),
            ('salary', 'incom', 3, 422),  # Неправильное имя категории
            ('salary', 'income', 3, 400),  # Повторяющееся имя категории
        ]
    )
    async def test_add_category(
            self, ac: AsyncClient, token, name, group, position, status_code
    ):
        response = await ac.post(
            "/api/categories",
            json=
            {
                "name": name,
                "group": group,
                "icon": "string"
            },
            cookies={'value': token}
        )

        # response = await ac.get(
        #     "/api/categories/test",
        # )
        # print(f'{response=}')
        category = response.json()
        assert response.status_code == status_code
        if status_code == 200:
            assert category['position'] == position

    @pytest.mark.parametrize(
        'id, status_code',
        [
            (1, 200),
            (5, 200),
            (4, 200),
            (8, 200),
        ]
    )
    async def _test_remove_category(
            self, ac: AsyncClient, token, id, status_code
    ):
        response = await ac.delete(
            f"/api/categories/?category_id={id}",
            cookies={'value': token}
        )

        assert response.status_code == 200
        group = response.json()['group']

        async with async_session() as db:
            query = select(Category).filter_by(group=group)
            categories = (await db.execute(query)).scalars().all()
            i = 1
            for category in sorted(categories, key=lambda x: x.position):
                assert category.position == i
                i += 1

