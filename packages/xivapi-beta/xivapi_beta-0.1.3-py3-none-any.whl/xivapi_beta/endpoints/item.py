import logging

from ..endpoints.asset import XIVAPIAsset
from .._wrapper import XIVAPIWrapper


# Configure module logging
module_logger = logging.getLogger(__name__)


class XIVAPIItem(XIVAPIWrapper):
    """
    An abstraction for interacting with specific rows from the Item sheet of XIVAPI.

    Parameters
    ----------
    item_data : dict
        The full row of data from the Item sheet.
    """

    # class logger
    _XIVAPIItem_logger = module_logger.getChild(__qualname__)

    def __init__(self, item_id: int, item_data: dict) -> None:
        super().__init__()
        # instance logger
        self._instance_logger = self._XIVAPIItem_logger.getChild(str(id(self)))

        self._data = item_data

        self.icon_data = item_data['Icon']
        self.icon = XIVAPIAsset(self.icon_data['path_hr1'])
        self.name = item_data['Name']
        self.item_id = item_id
        self.market_info = item_data['ItemSearchCategory']
        self.item_level_info = item_data['LevelItem']

    async def get_icon_file(self, path: str) -> str:
        """Create a file for this asset's icon starting at path."""
        return await self.icon.create_asset_file(path)

    async def get_icon_data(self) -> bytes:
        """Return the raw bytes data of this item's icon."""
        return await self.icon.asset_bytes()
