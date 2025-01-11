import logging
from collections.abc import Generator

import async_property

from .sheet import XIVAPISheet
from .._wrapper import XIVAPIWrapper
from ..exceptions import XIVAPIError
from .item import XIVAPIItem


# Configure module logging
module_logger = logging.getLogger(__name__)


class XIVAPISearchResult(XIVAPIWrapper):
    """A single result from an XIVAPI search."""

    def __init__(self, result_data: dict) -> None:
        super().__init__()
        self.score: float = result_data['score']
        self.sheet: XIVAPISheet = XIVAPISheet(result_data['sheet'])
        self.row_id: int = result_data['row_id']
        self.fields: dict = result_data['fields']

    @async_property.async_cached_property
    async def row(self) -> dict:
        """Get the full row for this search result."""
        row = await self.sheet.get_row(self.row_id)
        self.fields = row['fields']
        return self.fields


class XIVAPISearch(XIVAPIWrapper):
    """The full result of a search on XIVAPI's data."""

    _XIVAPISearchResult_logger = module_logger.getChild(__qualname__)

    def __init__(self, data: dict) -> None:
        # wrapper setup
        super().__init__()
        # logger
        self._instance_logger = self._XIVAPISearchResult_logger.getChild(str(id(self)))

        # initialize private vars
        self._pages: list[dict] = [data]

        self._instance_logger.debug("Search object created successfully")

    @property
    def first_page(self) -> dict:
        """
        The first full page of data of this result.

        Returns
        -------
        data : dict

        Raises
        ------
        XIVAPIError
            If you attempt to set data.
        """
        return self._pages[0]['results']

    @first_page.setter
    def first_page(self, _) -> None:
        raise XIVAPIError("Altering search result data is disallowed")

    async def _get_next_page(self, current_page: int) -> None:
        """
        Get the next page of results and store it in the pages dict.

        Parameters
        ----------
        current_page : int
            The current page

        Raises
        ------
        XIVAPIError
            If there is no next page to get
        """
        try:
            # check if the page is already cached
            self._pages[current_page + 1]
        except IndexError:
            # if it isn't, fetch it if there is a next page
            next_page_cursor = self._pages[current_page].get('next')
            if next_page_cursor is None:
                self._instance_logger.info("No next page to get")
                raise XIVAPIError("No next page to get")
            else:
                self._instance_logger.info("Fetching next page of results")
                next_page_data = await self.get_endpoint(
                    '/search',
                    params={'cursor': next_page_cursor}
                )
                self._pages[current_page + 1] = next_page_data
        else:
            # otherwise, just return
            return

    async def _get_pages(self, n: int = 10) -> None:
        """Get the first n pages of the result that exist."""
        current_page = 0
        while current_page <= n:
            try:
                await self._get_next_page(current_page)
            except XIVAPIError:
                break
            current_page += 1

    async def results(self, limit: int = 0) -> Generator[XIVAPISearchResult]:
        """
        Yield each result until specified limit.

        Parameters
        ----------
        limit : int, optional
            Yield results until this limit is reached. If unspecified or 0, will
            yield all results.

        Yields
        ------
        result : XIVAPISearchResult
        """
        # initialize loop vars
        total_results = 0
        current_page = 0
        results_page = self._pages[current_page]['results'].copy()

        while limit == 0 or total_results < limit:
            # loop while there's no limit, or while we're below it
            if not results_page:
                # if the results list is empty, get the next page of results
                try:
                    await self._get_next_page(current_page)
                except XIVAPIError:
                    # if there's no next page, break the loop
                    break
                else:
                    # otherwise, iterate the page count and reset the results list
                    current_page += 1
                    results_page = self._pages[current_page]['results'].copy()
            # yield the best result and pop it off the list, then iterate total
            yield XIVAPISearchResult(results_page.pop(0))
            total_results += 1

    async def best_results(self, count: int = 1) -> list[XIVAPISearchResult]:
        """
        Return a list of the first count results from the search.

        If the search yielded fewer results than count, will return the full list of
        results.

        Parameters
        ----------
        count : int, optional
            How many results to return

        Returns
        -------
        results : list[XIVAPISearchResult]
        """
        results = [result async for result in self.results(count)]
        return results

    async def best_result(self) -> XIVAPISearchResult:
        """
        Return the best result.

        Returns
        -------
        XIVAPISearchResult

        Raises
        ------
        XIVAPIError
            If this search has no results.
        """
        results = await self.best_results()
        if not results:
            raise XIVAPIError("No results found for this query.")
        else:
            return results[0]


class XIVAPIItemSearch(XIVAPISearch):
    """A Search object performed only on the Item sheet."""

    async def results(self, limit: int = 0) -> Generator[XIVAPIItem]:
        async for result in super().results(limit):
            row = await result.row
            yield XIVAPIItem(result.row_id, row)
