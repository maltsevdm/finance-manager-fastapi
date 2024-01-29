from httpx import AsyncClient

from tests.utils import get_token

categories = [
    {'name': 'products',
     'group': 'expense',
     'position': 1},
    {'name': 'transport',
     'group': 'expense',
     'position': 2},
    {'name': 'other',
     'group': 'expense',
     'position': 3},
    {'name': 'tinkoff black',
     'group': 'bank',
     'position': 1},
    {'name': 'tinkoff s7',
     'group': 'bank',
     'position': 2},
    {'name': 'alpha',
     'group': 'bank',
     'position': 3},
    {'name': 'parents',
     'group': 'income',
     'position': 1},
    {'name': 'salary',
     'group': 'income',
     'position': 2},
    # {'name': 'salary',
    #  'group': 'other_group',
    #  'position': 1},
]


async def post_add_category(ac, token, name, group):
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
    return response


async def test_add_categories(ac: AsyncClient):
    token = await get_token(ac)

    for category in categories:
        print(category)
        response = await post_add_category(ac, token, category['name'], category['group'])
        res_category = response.json()
        assert response.status_code == 200
        assert res_category['position'] == category['position']
