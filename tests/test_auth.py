from httpx import AsyncClient


async def test_register(ac: AsyncClient):
    response = await ac.post("/api/auth/register", json={
        "email": "string",
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "username": "string"
    })

    assert response.status_code == 201


async def get_token(ac: AsyncClient) -> str:
    response = await ac.post(
        'api/auth/jwt/login',
        data={
            'username': 'string',
            'password': 'string'
        },
    )

    assert response.status_code == 204

    cookie = response.headers['set-cookie']
    return cookie.split(';')[0].split('=')[1]


async def test_login(ac: AsyncClient):
    token = await get_token(ac)

    response = await ac.post(
        "/api/categories",
        json=
        {
            "name": "products",
            "group": "income",
            "icon": "string"
        },
        cookies={'value': token}
    )
    print(response)
    assert response.status_code == 200

# async def main():
#     async with AsyncClient(app=app, base_url="http://test",
#                            follow_redirects=True) as ac:
#         await test_login(ac)
#
#
# if __name__ == '__main__':
#     asyncio.run(main())
