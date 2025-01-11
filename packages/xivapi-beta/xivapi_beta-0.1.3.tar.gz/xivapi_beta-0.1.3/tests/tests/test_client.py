import pytest
import asyncio
import json
import random

from aioresponses import aioresponses
from xivapi_beta.client import XIVAPIClient
from xivapi_beta.endpoints.asset import XIVAPIAsset, XIVAPIAssetMap
from xivapi_beta.exceptions import XIVAPIError
from xivapi_beta.endpoints.search import XIVAPISearch


class TestXIVAPIClient:

    client = XIVAPIClient()

    @pytest.mark.asyncio
    async def test_sheets(self, sheets_list):
        sheets = await self.client.sheets
        assert sheets == sheets_list

    @pytest.mark.asyncio
    async def test_assets(self):
        asset = await self.client.assets('ui/icon/032000/032046_hr1.tex')
        assert isinstance(asset, XIVAPIAsset)

    @pytest.mark.asyncio
    async def test_map_assets(self):
        map_asset = await self.client.map_assets('s1d1', '00')
        assert isinstance(map_asset, XIVAPIAssetMap)

    @pytest.mark.asyncio
    async def test_search_bad_sheets(self):
        with pytest.raises(XIVAPIError) as api_error:
            search_result = await self.client.search(['blah'],
                                                     [])
    @pytest.mark.asyncio
    async def test_search_bad_queries(self):
        with pytest.raises(XIVAPIError) as api_error:
            search_result = await self.client.search(['Item'],
                                                     [('Name', 'NOT', 'blah')])

    @pytest.mark.asyncio
    async def test_search_with_fields(self,
                                      mocked_response,
                                      sheets_string,
                                      query_string,
                                      search_url,
                                      search_results_payload_fields):
        fields = ['Name', 'Icon']
        fields_string = ','.join(fields)
        url = f'{search_url}?query={query_string}&sheets={sheets_string}&fields={fields_string}'
        mocked_response.get(url, status=200, payload=search_results_payload_fields)
        data = await self.client.search(['Item'],
                                        [('Name', '~', 'archeo')],
                                        fields=fields)

        assert data.first_page == search_results_payload_fields['results']

    @pytest.mark.asyncio
    async def test_search_with_transient(self,
                                         mocked_response,
                                         search_url,
                                         search_results_payload_transient):
        transient = ['Tooltip', 'Description']
        sheets = ['Mount']
        queries = [('Singular', '~', 'chocobo')]
        sheets_string = ','.join(sheets)
        query_string = ' '.join([f'{k}{c}"{v}"' for k, c, v in queries])
        transient_string = ','.join(transient)
        url = f'{search_url}?query={query_string}&sheets={sheets_string}&transient={transient_string}'
        mocked_response.get(url, status=200, payload=search_results_payload_transient)
        data = await self.client.search(sheets, queries, transient=transient)

        assert search_results_payload_transient['results'] == data.first_page

    @pytest.mark.asyncio
    async def test_search_with_limit(self,
                                     mocked_response,
                                     search_url,
                                     search_results_payload,
                                     sheets_string,
                                     query_string):
        url = f'{search_url}?limit=5&query={query_string}&sheets={sheets_string}'
        payload = search_results_payload
        payload['results'] = payload['results'][:5]
        mocked_response.get(url, status=200, payload=payload)
        resp = await self.client.search(['Item'],
                                        [('Name', '~', 'archeo')],
                                        limit=5)
        assert resp.first_page == payload['results']

    @pytest.mark.asyncio
    async def test_search_results_type(self, mocked_search, search_data):
        search_result = await self.client.search(search_data['sheets'],
                                                 search_data['queries'])
        assert isinstance(search_result, XIVAPISearch)

    @pytest.mark.asyncio
    @pytest.mark.parametrize('limit,after',
                             [(random.randint(1,99),
                               random.randint(0, 99)) for _ in range(10)])
    async def test_get_sheet_rows_with_limit_and_after(self, mocked_response, item_sheet_data, limit, after):
        resp_rows = item_sheet_data['rows'].copy()[after:after + limit]
        resp_data = item_sheet_data.copy()
        resp_data['rows'] = resp_rows
        item_sheet_url = (f'{XIVAPIClient.base_url}/sheet/Item?'
                          f'limit={limit}&after={after}')
        mocked_response.get(item_sheet_url, status=200,
                            payload=resp_data)
        rows = await self.client.get_sheet_rows('Item', limit=limit, after=after)
        assert rows == item_sheet_data['rows'][after:after + limit]

    @pytest.mark.asyncio
    @pytest.mark.parametrize('rows',
                             [[random.randint(0,99) for _ in range(10)] for _ in range(10)])
    async def test_get_sheet_rows_specific_rows(self, mocked_response, item_sheet_data, rows):
        resp_rows = [item_sheet_data['rows'][x] for x in rows]
        resp_data = item_sheet_data.copy()
        resp_data['rows'] = resp_rows
        item_sheet_url = f'{XIVAPIClient.base_url}/sheet/Item?rows={",".join(map(str,rows))}'
        mocked_response.get(item_sheet_url, status=200,
                            payload=resp_data)
        result_rows = await self.client.get_sheet_rows('Item', rows=rows)
        assert result_rows == resp_rows

    @pytest.mark.asyncio
    async def test_get_sheet_rows_default(self, mocked_response, item_sheet_data):
        item_sheet_url = f'{XIVAPIClient.base_url}/sheet/Item'
        mocked_response.get(item_sheet_url, status=200, payload=item_sheet_data)
        result_rows = await self.client.get_sheet_rows('Item')
        assert result_rows == item_sheet_data['rows']

    @pytest.mark.asyncio
    async def test_get_row_error(self):
        with pytest.raises(XIVAPIError):
            await self.client.get_row('blah', 2)

    @pytest.fixture
    def mocked_item_sheet_response(self, mocked_response, sheet_url, item_sheet_row):
        item_sheet_url = f'{sheet_url}/Item/{item_sheet_row["row_id"]}'
        mocked_response.get(item_sheet_url, status=200, payload=item_sheet_row)

    @pytest.mark.asyncio
    async def test_get_row(self, mocked_item_sheet_response, item_sheet_row):
        item_id = item_sheet_row['row_id']
        row_response = await self.client.get_row('Item', item_id)
        assert row_response == item_sheet_row

    @pytest.mark.asyncio
    async def test_get_item(self, mocked_search, mocked_item_sheet_response, item_sheet_row):
        item_name = "archeo"
        result = await self.client.get_item(item_name)

        assert result._data == item_sheet_row['fields']
