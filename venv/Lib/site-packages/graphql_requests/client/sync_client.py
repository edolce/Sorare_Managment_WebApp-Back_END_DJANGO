from typing import Any, Dict, Union

import requests

from graphql_requests.client.base import BaseClient
from graphql_requests.errors import GraphQLError
from graphql_requests.utils import dict_keys_to_snake_case_recursively


class Client(BaseClient):
    """
    Synchronous GraphQL request client.
    """

    def send(
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
        Send request to outer Graphql service and return received data
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

        response = requests.post(
            url,
            data=request_data,
            headers=headers,
            cookies=cookies,
            timeout=self._timeout,
        )
        response_data = response.json()

        errors = response_data.get("errors")
        if errors:
            raise GraphQLError(errors=errors)

        if self._auto_snake_case:
            return dict_keys_to_snake_case_recursively(
                response_data["data"], snake_case_serializer=self._snake_case_serializer
            )

        return response_data["data"]
