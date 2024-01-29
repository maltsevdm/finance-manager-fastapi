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


# async def main():
#     async with AsyncClient(app=app, base_url="http://test",
#                            follow_redirects=True) as ac:
#         await test_login(ac)
#
#
# if __name__ == '__main__':
#     asyncio.run(main())
