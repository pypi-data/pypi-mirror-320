import pytest
import json

from aioresponses import aioresponses
from xivapi_beta.client import XIVAPIClient

@pytest.fixture
def sheet_url():
    return XIVAPIClient.base_url + '/sheet'

@pytest.fixture
def search_url():
    return XIVAPIClient.base_url + '/search'

with open('tests/sheet.json', 'r') as f:
    SHEETS_LIST_GLOBAL = json.load(f)

@pytest.fixture
def sheets_list():
    return SHEETS_LIST_GLOBAL

with open('tests/search_results.json', 'r') as f:
    SEARCH_RESULTS_PAYLOAD_GLOBAL = json.load(f)

with open('tests/search_results_2.json', 'r') as f:
    SEARCH_RESULTS_PAYLOAD_2_GLOBAL = json.load(f)

@pytest.fixture
def search_results_payload():
    return SEARCH_RESULTS_PAYLOAD_GLOBAL

@pytest.fixture
def search_results_payload_2():
    return SEARCH_RESULTS_PAYLOAD_2_GLOBAL

with open('tests/search_results_fields.json', 'r') as f:
    SEARCH_RESULTS_PAYLOAD_FIELDS = json.load(f)

@pytest.fixture
def search_results_payload_fields():
    return SEARCH_RESULTS_PAYLOAD_FIELDS

with open('tests/search_results_transient.json', 'r') as f:
    SEARCH_RESULTS_PAYLOAD_TRANSIENT = json.load(f)

@pytest.fixture
def search_results_payload_transient():
    return SEARCH_RESULTS_PAYLOAD_TRANSIENT

with open('tests/Item.json', 'r') as f:
    ITEM_SHEET_DATA_GLOBAL = json.load(f)

@pytest.fixture
def item_sheet_data():
    return ITEM_SHEET_DATA_GLOBAL

with open('tests/response.json', 'r') as f:
    ITEM_SHEET_ROW = json.load(f)

@pytest.fixture
def item_sheet_row():
    return ITEM_SHEET_ROW

@pytest.fixture
def search_data():
    return {
        'sheets': ['Item'],
        'queries': [('Name', '~', 'archeo')]
    }

# RESPONSES
PASSTHROUGH_LIST = [
    f'{XIVAPIClient.base_url}/asset'
]
@pytest.fixture
def mocked_response():
    with aioresponses(passthrough=PASSTHROUGH_LIST) as m:
        yield m

@pytest.fixture(autouse=True)
def mocked_sheets(mocked_response, sheet_url, sheets_list):
    mocked_response.get(sheet_url, status=200, payload=sheets_list)

@pytest.fixture
def sheets_string(search_data):
    return ','.join(search_data['sheets'])

@pytest.fixture
def query_string(search_data):
    return ' '.join([f'{k}{c}"{v}"' for k, c, v in search_data['queries']])

@pytest.fixture
def mocked_search(mocked_response, search_data, search_url, sheets_string, query_string, search_results_payload):
    search_url_string = f'{search_url}?query={query_string}&sheets={sheets_string}'
    mocked_response.get(search_url_string, status=200,
                        payload=search_results_payload)