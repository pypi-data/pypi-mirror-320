import logging

import aiohttp

from .exceptions import XIVAPIError


# configure module logging
module_logger = logging.getLogger(__name__)


class XIVAPIWrapper:
    """
    Wrapper class for XIVAPI objects.

    Parameters
    ----------
    session : aiohttp.ClientSession, optional
        A `ClientSession` object to use for handling requests.

    Attributes
    ----------
    base_url : str
        The base URL for XIVAPI.com
    query_comparators : tuple[str]
        The valid comparators to use for search requests.
    asset_formats : tuple[str]
        The valid asset formats for non-map assets.
    """

    base_url: str = "https://beta.xivapi.com/api/1"
    query_comparators: tuple[str] = (
        "=",
        "~",
        ">",
        ">=",
        "<",
        "<="
    )
    asset_formats: tuple[str] = (
        'jpg',
        'png',
        'webp'
    )
    _XIVAPIWrapper_logger = module_logger.getChild(__qualname__)

    def __init__(self, *, session: aiohttp.ClientSession | None = None) -> None:
        self._session: aiohttp.ClientSession = session
        # instance logger
        self._instance_logger = self._XIVAPIWrapper_logger.getChild(str(id(self)))

    @property
    def session(self) -> aiohttp.ClientSession:
        """
        Retrieve the ``aiohttp.ClientSession`` object for this wrapper.

        Returns
        -------
        session : aiohttp.ClientSession
        """
        if self._session is None or self._session.closed:
            self._instance_logger.debug("Creating new aiohttp ClientSession object")
            self._session = aiohttp.ClientSession()
        return self._session

    async def _process_response(self, response: aiohttp.ClientResponse) -> None:
        """
        Raise an error if status code is not 200.

        Parameters
        ----------
        response : aiohttp.ClientResponse
            A ``ClientResponse`` to check for error codes.

        Raises
        ------
        XIVAPIError
            When response.stats != 200
        """
        if response.status != 200:
            self._instance_logger.warning("Non-200 response code received",
                                          extra={'response_code': response.status})
            raise XIVAPIError(f"{response.status} code received: {response.url}")
        else:
            self._instance_logger.info("200 code received, processing complete")
            return # explicit return here for clarity

    @staticmethod
    def _construct_params(**kwargs: str | int | list) -> dict:
        """
        Construct a valid parameters dict from the given kwargs.

        Parameters
        ----------
        kwargs : str | int | list

        Returns
        -------
        params : dict
        """
        params = {}
        for key, value in kwargs.items():
            if value is None:
                pass
            else:
                match key:
                    case "sheets" | "rows" | "fields" | "transient":
                        params[key] = ','.join(map(str, value))
                    case "limit":
                        if value > 0:
                            params[key] = value
                    case "query":
                        params[key] = ' '.join([f'{k}{c}"{v}"' for k, c, v in value])
                    case _:
                        params[key] = value
        return params

    async def get_endpoint(self,
                           endpoint: str, *,
                           params: dict[str, str] = None,
                           json: bool = True) -> dict | list | bytes:
        """
        Retrieve data from the given XIVAPI endpoint as JSON (or bytes if specified).

        Parameters
        ----------
        endpoint : str
            The endpoint relative to `base_url`.
        params : dict[str, str], optional
            A dict of parameters to pass to the `get` request.
        json : bool, optional
            Whether response should be parsed in JSON, default True.

        Returns
        -------
        response_data : dict | list | bytes
            A dict or list if JSON was requested, or bytes if not.

        Raises
        ------
        XIVAPIError
            When response can't be parsed.
        """
        #generate full url
        url = self.base_url + endpoint
        if params is None:
            params = {}
        self._instance_logger.debug("Sending endpoint request",
                                    extra={'url': url, 'params': params})

        async with self.session as session:
            async with session.get(url, params=params) as response:
                self._instance_logger.debug("Response created, processing object")
                await self._process_response(response)
                # try to get the data
                try:
                    if json:
                        data = await response.json()
                    else:
                        data = await response.read()
                except aiohttp.ContentTypeError as e:
                    # catch JSON errors
                    self._instance_logger.warning(
                        "JSON data expected, but not received",
                        extra={'content-type': response.content_type,
                               'error': e})
                    raise XIVAPIError(e)
                except aiohttp.ClientResponseError as e:
                    # catch bytes errors
                    self._instance_logger.warning(
                        "Bytestream could not be read",
                        extra={'content-type': response.content_type,
                               'error': e})
                    raise XIVAPIError(e)
                else:
                    return data
