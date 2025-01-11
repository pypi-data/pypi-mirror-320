import pytest
import random

from xivapi_beta.client import XIVAPIClient
from xivapi_beta.endpoints.search import XIVAPISearch
from xivapi_beta.exceptions import XIVAPIError


class TestXIVAPISearchResult:
    client = XIVAPIClient()
    dummy_result = XIVAPISearch({})

    @pytest.fixture
    def mocked_search_pages(self, mocked_response, search_data, search_results_payload, search_results_payload_2):
        search_url = f'{self.client.base_url}/search'
        query_string = ' '.join([f'{k}{c}"{v}"' for k, c, v in search_data['queries']])
        sheets_string = ','.join(search_data['sheets'])
        first_search_url = f'{search_url}?query={query_string}&sheets={sheets_string}'
        cursor_search_url = f'{search_url}?cursor={search_results_payload["next"]}'
        mocked_response.get(f'{first_search_url}', status=200, payload=search_results_payload)
        mocked_response.get(f'{first_search_url}', status=200, payload=search_results_payload)
        mocked_response.get(f'{cursor_search_url}', status=200,
                            payload=search_results_payload_2)

    @pytest.mark.asyncio
    async def test_data(self, mocked_search, search_data, search_results_payload):
        search_result = await self.client.search(search_data['sheets'],
                                                 search_data['queries'])
        data = search_result.data
        assert search_results_payload == data

    def test_data_set(self):
        with pytest.raises(XIVAPIError):
            self.dummy_result.data = {}

    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_full_search(self, mocked_search_pages, search_data, search_results_payload, search_results_payload_2):
        search_result = await self.client.search(search_data['sheets'],
                                                 search_data['queries'])

        await search_result.search(full=True)

        pages = {1: search_results_payload,
                 2: search_results_payload_2}

        assert pages == search_result._pages

    @pytest.mark.asyncio
    @pytest.mark.parametrize("n", [random.randint(1,30) for _ in range(10)])
    async def test_get_results(self, n, mocked_search, search_data, search_results_payload):
        search_result = await self.client.search(search_data['sheets'],
                                                 search_data['queries'])
        results = [res async for res in search_result.results(n)]
        assert results == search_results_payload['results'][:n]

    @pytest.mark.asyncio
    async def test_get_results_full_gen(self, mocked_search_pages, search_data, search_results_payload, search_results_payload_2):
        search_result = await self.client.search(search_data['sheets'],
                                                 search_data['queries'])
        results = [res async for res in search_result.results()]
        test_results = search_results_payload['results'].copy()
        test_results.extend(search_results_payload_2['results'])
        assert results == test_results

    @pytest.mark.asyncio
    @pytest.mark.parametrize("n", [random.randint(1,30) for _ in range(10)])
    async def test_best_results(self, n, mocked_search, search_data, search_results_payload):
        search_result = await self.client.search(search_data['sheets'],
                                                 search_data['queries'])
        results = await search_result.best_results(n)
        assert results == search_results_payload['results'][:n]

    @pytest.mark.asyncio
    async def test_best_result(self, mocked_search, search_data, search_results_payload):
        search_result = await self.client.search(search_data['sheets'],
                                                 search_data['queries'])
        result = await search_result.best_result()
        assert result == search_results_payload['results'][0]
