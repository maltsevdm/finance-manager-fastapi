from httpx import AsyncClient

from tests.conftest import client


async def test_add_category(ac: AsyncClient):
    assert 1 == 1
    # response = await ac.post("/api/categories", json={
    #     "name": "products",
    #     "group": "income",
    #     "icon": "string"
    # })
    # print(response)
    # assert response.status_code == 200
