import json
from types import TracebackType
from typing import Any, Dict, Optional, Type, Union

from aiohttp import ClientResponse, ClientSession, ClientTimeout

from graphql_requests.client.base import BaseClient
from graphql_requests.errors import ClientAlreadyConnected, GraphQLError
from graphql_requests.typedefs import JSONEncoder, SnakeCaseEncoder
from graphql_requests.utils import dict_keys_to_snake_case_recursively, to_snake_case


class AsyncClient(BaseClient):
    """
    Asynchronous GraphQL request client.
    """

    def __init__(
        self,
        base_url: Union[str, None] = None,
        *,
        headers: Union[Dict[str, Any], None] = None,
        cookies: Union[Dict[str, Any], None] = None,
        json_serialize: Union[JSONEncoder, None] = json.dumps,
        snake_case_serializer: Union[SnakeCaseEncoder, None] = to_snake_case,
        auto_snake_case: Union[bool, None] = True,
        timeout: Union[float, None] = None,
        session_args: Union[Dict[str, Any], None] = None,
    ) -> None:
        self._session_args = session_args or {}
        self._session: Union[ClientSession, None] = None

        super().__init__(
            base_url,
            headers=headers,
            cookies=cookies,
            json_serialize=json_serialize,
            snake_case_serializer=snake_case_serializer,
            auto_snake_case=auto_snake_case,
            timeout=timeout,
        )

    async def send(
        self,
        url: Union[str, None] = None,
        *,
        query: str,
        operation_name: str = None,
        variables: Union[str, Dict[str, Any]] = None,
        headers: Union[Dict[str, Any], None] = None,
        cookies: Union[Dict[str, Any], None] = None,
    ) -> Dict[str, Any]:
        """
        Send request to outer Graphql service asynchronously and return received data
        """
        if headers is None:
            headers = dict()
        if cookies is None:
            cookies = dict()
        headers.update(self._headers or {})
        cookies.update(self._cookies or {})

        # concatenation `_base_url` (that initialized with client) with arg `url`
        if url is not None:
            url = self._base_url.rstrip("/") + "/" + url.lstrip("/")
        else:
            url = self._base_url

        request_data = self._build_send_data(
            query=query, operation_name=operation_name, variables=variables
        )

        async with self._session.post(
            url,
            data=request_data,
            headers=headers,
            cookies=cookies,
        ) as response:
            response: ClientResponse
            response_data = await response.json()

        errors = response_data.get("errors")
        if errors:
            raise GraphQLError(errors=errors)

        if self._auto_snake_case:
            return dict_keys_to_snake_case_recursively(
                response_data["data"], snake_case_serializer=self._snake_case_serializer
            )

        return response_data["data"]

    async def connect(self) -> None:
        """
        Connect to the client session. May be used with `async with` statement.

        Warning! Do not connect to a new session, when old is unclosed.
        """
        if self._session is not None:
            raise ClientAlreadyConnected(
                "You are trying to override an unclosed client session"
            )

        session_args = dict(
            headers=self._headers,
            cookies=self._cookies,
            json_serialize=self._json_serialize,
        )

        session_args.update(self._session_args)

        if self._timeout is not None:
            session_args["timeout"] = ClientTimeout(total=self._timeout)

        self._session = ClientSession(**session_args)

    async def close(self) -> None:
        """
        Close client session if it exists. May be used with `async with` statement.
        """
        if self._session is None:
            return

        if not self._session.closed:
            await self._session.close()

        self._session = None

    def __enter__(self) -> None:
        raise TypeError("Use `async with` instead")

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        # __exit__ should exist in pair with __enter__ but never executed
        pass

    async def __aenter__(self) -> "AsyncClient":
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.close()
