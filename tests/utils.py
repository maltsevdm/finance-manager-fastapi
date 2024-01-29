from httpx import AsyncClient


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