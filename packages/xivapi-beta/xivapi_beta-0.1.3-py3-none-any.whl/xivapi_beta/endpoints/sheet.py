from .._wrapper import XIVAPIWrapper


class XIVAPISheet(XIVAPIWrapper):
    """A wrapper for interacting with XIVAPI's /sheet endpoint."""

    def __init__(self, sheet_name: str) -> None:
        super().__init__()
        self.sheet_name = sheet_name

    async def get_row(self, row_id: int | str, *,
                      fields: list[str] | None = None,
                      transient: list[str] | None = None) -> dict:
        """
        Return the requested row from this sheet.

        Parameters
        ----------
        row_id : int | str
            The row to retrieve.

        Returns
        -------
        row : dict
            The data from the requested row.

        Raises
        ------
        XIVAPIError
            If the row_id does not exist in this sheet.

        Other Parameters
        ----------------
        fields : list[str], optional
            A list of fields to return in the row. If this is specified, **ONLY** these
            fields will be returned.
        transient : list[str], optional
            A list of transient fields to return in the row.
        """
        params = self._construct_params(
            fields=fields,
            transient=transient
        )

        endpoint = f'/sheet/{self.sheet_name}/{row_id}'

        row = await self.get_endpoint(endpoint, params=params)
        return row

    async def get_sheet_rows(self, *,
                             row_ids: list[int | str] | None = None,
                             limit: int = 0,
                             after: int | None = None,
                             fields: list[str] | None = None,
                             transient: list[str] | None = None) -> list[dict]:
        """
        Return a list of rows from this sheet.

        If `limit` and `rows` are unspecified, return the first 100 rows.

        Returns
        -------
        rows : list[dict]
            A list of rows from the sheet.

        Other Parameters
        ----------------
        row_ids : list[int | str], optional
            A list of row IDs to retrieve. If this is specified, **ONLY** these rows
            will be returned. Note that this will not return *all* fields for these
            rows. For that functionality see ``get_row``.
        limit : int
            The number of rows to retrieve.
        after : int
            Return `limit` rows after this row.
        fields : list[str]
            List of fields to return for each row. Default fields generally include
            'Icon' and 'Name'
        transient : list[str]
            List of transient fields to return for each row.
        """
        params = self._construct_params(
            rows=row_ids,
            limit=limit,
            after=after,
            fields=fields,
            transient=transient
        )
        row_data = await self.get_endpoint(f'/sheet/{self.sheet_name}',
                                           params=params)
        return row_data['rows']
