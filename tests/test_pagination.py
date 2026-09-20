import pytest

from app import config

LIST_ENDPOINTS = ["/movies/", "/locations/", "/movie-locations/"]


@pytest.mark.parametrize("path", LIST_ENDPOINTS)
@pytest.mark.parametrize("limit", [0, -1, config.MAX_PAGE_SIZE + 1, 10_000_000])
def test_limit_out_of_range_is_rejected(client, path, limit):
    assert client.get(path, params={"limit": limit}).status_code == 400


@pytest.mark.parametrize("path", LIST_ENDPOINTS)
@pytest.mark.parametrize("limit", [1, 100, config.MAX_PAGE_SIZE])
def test_limit_within_range_is_accepted(client, path, limit):
    assert client.get(path, params={"limit": limit}).status_code == 200
