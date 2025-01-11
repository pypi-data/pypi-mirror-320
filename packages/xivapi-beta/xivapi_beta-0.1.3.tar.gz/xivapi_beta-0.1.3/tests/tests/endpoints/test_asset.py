import aiohttp
import pytest
from unittest.mock import AsyncMock

from aioresponses import aioresponses

from xivapi_beta.client import XIVAPIClient
from xivapi_beta.endpoints.asset import XIVAPIAsset, XIVAPIAssetMap


class TestXIVAPIAsset:
    asset = XIVAPIAsset('ui/icon/032000/032046_hr1.tex')
    map_asset = XIVAPIAssetMap('s1d1', '00')
    with open('tests/icon.png', 'rb') as f:
        asset_bytes = f.read()
    with open('tests/map.jpg', 'rb') as f:
        map_bytes = f.read()

    @pytest.mark.asyncio
    async def test_asset_bytes(self):
        data = await self.asset.asset_bytes()
        assert data == self.asset_bytes

    @pytest.mark.asyncio
    async def test_asset_bytes_map(self):
        data = await self.map_asset.asset_bytes()
        assert data == self.map_bytes

    @pytest.mark.asyncio
    async def test_create_asset_file(self, mocker):
        test_asset_path = '/home/stoye'
        mock_file = mocker.mock_open()
        mocker.patch("builtins.open", mock_file)
        return_file_path = await self.asset.create_asset_file(test_asset_path)

        mock_file.assert_called_once_with(f'{test_asset_path}/032046_hr1.png', 'wb')
        mock_file().write.assert_called_once_with(self.asset_bytes)
        assert return_file_path == f'{test_asset_path}/032046_hr1.png'

    @pytest.mark.asyncio
    async def test_create_asset_file_map(self, mocker):
        test_map_path = '/home/stoye'
        mock_file = mocker.mock_open()
        mocker.patch("builtins.open", mock_file)
        return_file_path = await self.map_asset.create_asset_file(test_map_path)

        mock_file.assert_called_once_with(f'{test_map_path}/s1d1_00.jpg', 'wb')
        mock_file().write.assert_called_once_with(self.map_bytes)
        assert return_file_path == f'{test_map_path}/s1d1_00.jpg'
