import logging

import aiohttp
import async_property

from .endpoints.sheet import XIVAPISheet
from .exceptions import XIVAPIError
from .endpoints.asset import XIVAPIAsset, XIVAPIAssetMap
from .endpoints.search import XIVAPISearch, XIVAPIItemSearch
from .endpoints.item import XIVAPIItem
from ._wrapper import XIVAPIWrapper


# Configure module logging
module_logger = logging.getLogger(__name__)


type Query = tuple[str, str, str | int | float | bool]
"""Queries are tuples containing a key, a comparator, and a value."""


class XIVAPIClient(XIVAPIWrapper):
    """
    Asynchronous client for accessing XIVAPI's beta endpoints.

    Supported endpoints:
        - assets
            - XIVAPIClient.assets will return an XIVAPIAsset object for general assets,
            maps to /asset endpoint
            - XIVAPIClient.map_assets will return an XIVAPIAssetMap object for map jpgs,
            maps to /asset/map endpoint
        - search
            - XIVAPIClient.search will perform a search query on XIVAPI's sheets, maps
            to /search endpoint
        - sheets
            - XIVAPIClient.sheets will return a list[str] of sheet names in XIVAPI, maps
            to /sheets endpoint
            - XIVAPIClient.get_sheet_rows maps to /sheets/{sheet} endpoint
            - XIVAPIClient.get_row maps to /sheets/{sheet}/{row_id} endpoint
    """

    _XIVAPIClient_logger = module_logger.getChild(__qualname__)

    def __init__(self, *, session: aiohttp.ClientSession | None = None) -> None:
        super().__init__(session=session)

        # instance logger
        self._instance_logger = self._XIVAPIClient_logger.getChild(str(id(self)))
        self._instance_logger.debug("XIVAPIClient Created")

        self._sheets: list[str] = []

    @async_property.async_cached_property
    async def sheets(self) -> list[str]:
        """
        Get a list of searchable sheets on XIVAPI.

        Response will be cached once fetched.

        Returns
        -------
        sheets : list[str]
        """
        if not self._sheets:
            self._instance_logger.debug("Fetching /sheet endpoint")
            self._sheets = await self.get_endpoint('/sheet')
        return self._sheets

    @staticmethod
    async def assets(asset_path: str, *, fmt: str = 'png') -> XIVAPIAsset:
        """
        Return an XIVAPIAsset for the given asset path.

        Parameters
        ----------
        asset_path : str
            The path for the asset to retrieve. This is usually received from a
            different XIVAPI request.
        fmt : str, optional
            The format to convert the asset into. Must be one of
            `XIVAPIClient.asset_formats`.

        Returns
        -------
        XIVAPIAsset
        """
        return XIVAPIAsset(asset_path, fmt)

    @staticmethod
    async def map_assets(territory: str, index: str) -> XIVAPIAssetMap:
        """
        Return an XIVAPIAssetMap for the given territory and index.

        Parameters
        ----------
        territory : str
        index : str

        Returns
        -------
        XIVAPIAssetMap
        """
        return XIVAPIAssetMap(territory, index)

    async def _search(self,
                      sheets: list[str],
                      queries: list[Query], *,
                      limit: int = 0,
                      fields: list[str] | None = None,
                      transient: list[str] | None = None) -> dict:
        """Search XIVAPI."""
        # sanitize the sheets and queries by checking that each sheet provided is valid
        # and each query uses valid comparators
        self._instance_logger.debug("Starting sanitization")
        sheets = await self._sanitize_sheets(sheets)
        queries = self._sanitize_queries(queries)
        self._instance_logger.debug("Sanitization complete",
                                    extra={'sheets': sheets, 'queries': queries})

        # create the params to be passed to the ClientSession
        params = self._construct_params(
            sheets=sheets,
            query=queries,
            fields=fields,
            transient=transient,
            limit=limit
        )
        self._instance_logger.debug("Search params constructed",
                                    extra={'params': params})

        # run the search
        self._instance_logger.info("Searching!")
        search_data = await self.get_endpoint("/search", params=params)
        return search_data

    async def search(self,
                     sheets: list[str],
                     queries: list[Query], *,
                     limit: int = 0,
                     fields: list[str] = None,
                     transient: list[str] = None) -> XIVAPISearch:
        """
        Perform a search on the XIVAPI on the given sheets with the given queries.

        This returns an XIVAPISearchResult that can be interacted with dynamically
        abstracting away the need to know how data is formatted in the API.

        Parameters
        ----------
        sheets : list[str]
            A list of sheets to search over.
        queries : list[Query]
            A list of queries to perform on each sheet.

        Returns
        -------
        search_result : XIVAPISearch
            A search result object.

        Other Parameters
        ----------------
        limit : int, optional
            How many items to return per page of the search result.
        fields : list[str], optional
            A list of fields to include for each result.
        transient : list[str], optional
            A list of transient fields to include for each result.
        """
        search_data = await self._search(sheets, queries, limit=limit, fields=fields,
                                         transient=transient)
        # raise error if there are no results
        if not search_data['results']:
            self._instance_logger.warning("No results found.")
            raise XIVAPIError("No results found.")
        else:
            # otherwise generate and return the search object
            return XIVAPISearch(search_data)

    async def _sanitize_sheets(self, sheets: list[str]) -> list[str]:
        """
        Remove any invalid sheets from the given list.

        Parameters
        ----------
        sheets : list[str]
            List of sheets to check.

        Returns
        -------
        sheets : list[str]
            List of sheets that are valid.

        Raises
        ------
        XIVAPIError
            If all sheets are invalid.
        """
        valid_sheets = await self.sheets
        sanitized_sheets = []
        for sheet in sheets:
            if sheet not in valid_sheets:
                self._instance_logger.info(
                    "Sheet is not in list of valid sheets",
                    extra={'sheet': sheet}
                )
                pass
            else:
                sanitized_sheets.append(sheet)
        if not sanitized_sheets:
            raise XIVAPIError("No valid searchable sheets provided")
        else:
            return sanitized_sheets

    def _sanitize_queries(self, queries: list[Query]) -> list[Query]:
        """
        Remove any invalid queries from the given list.

        Parameters
        ----------
        queries : list[Query]
            List of queries to check.

        Returns
        -------
        queries : list[Query]
            List of valid queries.

        Raises
        ------
        XIVAPIError
            If all queries are malformed.
        """
        sanitized_queries = []
        for query in queries:
            if query[1] not in self.query_comparators:
                self._instance_logger.info(
                    "Unsupported comparator",
                    extra={'query': query}
                )
                pass
            else:
                sanitized_queries.append(query)
        if not sanitized_queries:
            raise XIVAPIError("All queries malformed")
        else:
            return sanitized_queries

    async def get_sheet_rows(self,
                             sheet: str, *,
                             rows: list[int] = None,
                             limit: int = 0,
                             after: int = None,
                             fields: list[str] = None,
                             transient: list[str] = None) -> list[dict]:
        """
        Return a list of rows from the given sheet.

        If no other parameters are specified, return the first 100 rows.

        Parameters
        ----------
        sheet : str
            The sheet to get rows from

        Returns
        -------
        rows : list[dict]
            A list of rows from the sheet.

        Other Parameters
        ----------------
        rows : list[int | str], optional
            A list of row IDs to retrieve. If this is specified, **ONLY** these rows
            will be returned. Note that this will not return *all* fields for these
            rows. For that functionality see ``get_row``.
        limit : int
            The number of rows to retrieve.
        after : int
            Return `limit` rows after this row.
        fields : list[str]
            List of fields to return for each row.
        transient : list[str]
            List of transient fields to return for each row.
        """
        # make sure sheets are cached
        valid_sheets = await self.sheets
        # check sheet validity
        if sheet not in valid_sheets:
            self._instance_logger.warning("Requested sheet is invalid",
                                          extra={'sheet': sheet})
            raise XIVAPIError(f"{sheet} is not a valid XIVAPI sheet")

        sheet = XIVAPISheet(sheet)
        return await sheet.get_sheet_rows(row_ids=rows, limit=limit, after=after,
                                          fields=fields, transient=transient)

    async def get_row(self,
                      sheet: str,
                      row_id: int | str, *,
                      fields: list[str] = None,
                      transient: list[str] = None) -> dict:
        """
        Return the requested row from the requested sheet.

        If `fields` is not specified, returns all fields.

        Parameters
        ----------
        sheet : str
            The sheet to get the row from.
        row_id : int | str
            The row to retrieve.

        Returns
        -------
        row : dict
            The data from the requested row.

        Other Parameters
        ----------------
        fields : list[str], optional
            A list of fields to return in the row. If this is specified, **ONLY** these
            fields will be returned.
        transient : list[str], optional
            A list of transient fields to return in the row.
        """
        # make sure sheets are cached
        sheets = await self.sheets
        # check sheet validity
        if sheet not in sheets:
            self._instance_logger.warning("Requested sheet is invalid",
                                          extra={'sheet': sheet})
            raise XIVAPIError(f"{sheet} is not a valid XIVAPI sheet")

        sheet = XIVAPISheet(sheet)
        return await sheet.get_row(row_id, fields=fields, transient=transient)

    # the following are not endpoints but rather convenience functions provided by this
    # library

    async def item_search(self, item_name: str) -> XIVAPIItemSearch:
        """
        Return a list of item objects that best match the given name.

        This performs a bare-bones search on the Item sheet with the given string as the
        query on the Name field. Use `search` if you desire more functionality.

        Parameters
        ----------
        item_name : str
            The item to search for.

        Returns
        -------
        XIVAPIItemSearch
        """
        sheets = ['Item']
        queries = [('Name', '~', item_name)]
        search_data = await self._search(sheets, queries)
        return XIVAPIItemSearch(search_data)

    async def get_item(self, item_name: str) -> XIVAPIItem:
        """
        Return an XIVAPIItem object that best matches the given item name.

        This is an abstraction layer for performing an api search with the given item
        name, retrieving the best result, and getting the full result row and storing
        it in an XIVAPIItem object.

        Parameters
        ----------
        item_name : str
            The item to search for.

        Returns
        -------
        item : XIVAPIItem
        """
        # search time
        search_obj = await self.search(['Item'], [('Name', '~', item_name)])
        try:
            result = await search_obj.best_result()
        except XIVAPIError as e:
            self._instance_logger.info("No item found with given name",
                                       extra={'name': item_name})
            raise XIVAPIError(e)
        else:
            item_row = await result.row
            return XIVAPIItem(result.row_id, item_row)
