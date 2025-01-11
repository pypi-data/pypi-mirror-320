import random

import aiohttp
import pytest

from xivapi_beta.exceptions import XIVAPIError
from xivapi_beta._wrapper import XIVAPIWrapper


class TestXIVAPIWrapper:
    wrapper = XIVAPIWrapper()

    @pytest.mark.asyncio
    async def test_session(self):
        async with self.wrapper.session as session:
            assert isinstance(session, aiohttp.ClientSession)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("code", [random.randint(300,500) for _ in range(10)])
    async def test_process_response_failure(self, code, mocked_response):
        mocked_response.get(f'{self.wrapper.base_url}/test', status=code)
        with pytest.raises(XIVAPIError):
            async with self.wrapper.session as session:
                async with session.get(f'{self.wrapper.base_url}/test') as resp:
                    await self.wrapper._process_response(resp)

    @pytest.mark.asyncio
    async def test_get_endpoint(self, sheets_list):
        resp = await self.wrapper.get_endpoint('/sheet')
        assert resp == sheets_list
