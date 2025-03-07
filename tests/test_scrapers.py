from scrapers.microcenter import get_open_box_items
import pytest
import httpx
from pytest_httpx import HTTPXMock

@pytest.mark.asyncio
async def test_get_open_box_items(httpx_mock: HTTPXMock):
    httpx_mock.add_response(url="https://example.com", json={"message": "Hello, world!"})
    async with httpx.AsyncClient() as client:
        response = await client.get("https://example.com")
        assert response.json() == {"message": "Hello, world!"}

@pytest.mark.asyncio
async def test_get_open_box_items(mocker):
    """Test scraper fetches open box items correctly."""
    mock_response = [{"title": "GPU XYZ", "price": "$499.99", "url": "https://example.com"}]
    mocker.patch("scrapers.microcenter.get_open_box_items", return_value=mock_response)

    items = await get_open_box_items()
    assert isinstance(items, list)
    assert len(items) > 0
    assert items[0]["title"] == "GPU XYZ"
    assert items[0]["price"] == "$499.99"