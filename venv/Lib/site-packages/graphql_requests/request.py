import re
from typing import Any, Dict

from graphql_requests.utils import (
    dict_keys_to_camel_case_recursively,
    read_scheme_from_file,
)


class GraphQLRequest:
    def __init__(self, *, body: str, variables: Dict[str, Any]) -> None:
        """
        Build request send data for outer GraphQL service
        """
        self._body = body
        self._variables = dict_keys_to_camel_case_recursively(variables)

    def set_variables(self, variables: Dict[str, Any]) -> "GraphQLRequest":
        """
        Override variables to send
        """
        camel_case_variables = dict_keys_to_camel_case_recursively(variables)

        return GraphQLRequest(body=self._body, variables=camel_case_variables)

    def extend_variables(
        self, additional_variables: Dict[str, Any]
    ) -> "GraphQLRequest":
        """
        Add new variables to existing ones
        """
        camel_case_variables = dict_keys_to_camel_case_recursively(additional_variables)
        camel_case_variables.update(self._variables)

        return GraphQLRequest(body=self._body, variables=camel_case_variables)

    def set_fragment(self, fragment: str) -> "GraphQLRequest":
        """
        Add GraphQL fragment to request body
        """
        clear_fragment = re.sub(r"[\n\r\s]{2,}", " ", fragment)
        new_body = "{} {}".format(self._body, clear_fragment)

        return GraphQLRequest(body=new_body, variables=self._variables)

    def set_scheme_from_file(
        self, file_path: str, *, encoding: str = "UTF-8"
    ) -> "GraphQLRequest":
        """
        Read scheme from file and set it to request body
        """
        body = read_scheme_from_file(file_path, encoding=encoding)

        return GraphQLRequest(body=body, variables=self._variables)

    @property
    def body(self) -> str:
        """
        Request scheme
        """
        return self._body

    @property
    def variables(self) -> Dict[str, Any]:
        """
        Request payload
        """
        return self._variables
