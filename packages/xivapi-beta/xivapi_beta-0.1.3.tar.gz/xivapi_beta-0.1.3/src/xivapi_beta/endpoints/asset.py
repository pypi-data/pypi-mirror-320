import logging
import os.path

import aiohttp

from .._wrapper import XIVAPIWrapper


# Configure module logging
module_logger = logging.getLogger(__name__)


class XIVAPIAsset(XIVAPIWrapper):
    """An object representing the response of a request to the /asset endpoint."""

    # class logger
    _XIVAPIAsset_logger = module_logger.getChild(__qualname__)

    def __init__(self, asset_path: str, fmt: str = 'png') -> None:
        super().__init__()
        # logger
        self._instance_logger = self._XIVAPIAsset_logger.getChild(str(id(self)))

        self._data = None

        self.asset_path = asset_path
        self.asset_name = self.asset_path.split('/')[3].split('.')[0]
        self.fmt = fmt
        self.params = {'path': asset_path, 'format': fmt}

    async def _get_asset_data(self) -> None:
        self._data = await self.get_endpoint('/asset',
                                             params=self.params,
                                             json=False)

    async def create_asset_file(self, base_path: str) -> str:
        """
        Create an icon file from this object's data.

        Assets will be created at base_path/asset_name.fmt.

        Parameters
        ----------
        base_path : str
            The base path to where this file should be stored.

        Returns
        -------
        path : str
            The full path to the created file.
        """
        icon_path = f'{base_path}/{self.asset_name}.{self.fmt}'
        if os.path.isfile(icon_path):
            # return the path if we've already got this icon file
            return icon_path
        else:
            with open(icon_path, 'wb') as icon_file:
                if self._data is None:
                    await self._get_asset_data()
                icon_file.write(self._data)
            return icon_path

    async def asset_bytes(self) -> bytes:
        """Return the byte data for this asset."""
        if self._data is None:
            await self._get_asset_data()
        return self._data


class XIVAPIAssetMap(XIVAPIAsset):
    """An object representing a map asset."""

    def __init__(self, territory: str, index: str) -> None:
        fmt = 'jpg'
        asset_path = f'/asset/map/{territory}/{index}'
        super().__init__(asset_path, fmt)

        self.asset_name = f'{territory}_{index}'

    async def _get_asset_data(self) -> None:
        self._data = await self.get_endpoint(self.asset_path, json=False)
