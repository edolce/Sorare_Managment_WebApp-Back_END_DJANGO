from os import path
from re import compile
from typing import Any, Dict

from graphql_requests.typedefs import SnakeCaseEncoder

SNAKE_CASE_PATTERN = compile(r"(?<!^)(?=[A-Z])")
SELECT_ABBREVIATIONS_PATTERN = compile(r"(.)([A-Z][a-z]+)")
SEPARATE_WORD_FORM_ABBREVIATIONS_PATTERN = compile(r"([a-z0-9])([A-Z])")


def to_snake_case(camel_str: str) -> str:
    """
    Convert string from `camelCase` to `snake_case`.

    Warning! String "getHTTPResponse" after processing will look like "get_h_t_t_p_response".
    For more complex cases (like above with multiple consecutive capital letters) use `to_snake_case_save` function.
    """
    return SNAKE_CASE_PATTERN.sub(r"_", camel_str).lower()


def to_snake_case_safe(camel_str: str) -> str:
    """
    Convert string from `camelCase` to `snake_case`
    with saving abbreviation (or any string with multiple consecutive capital letters).
    This operation take more time than usual `to_snake_case`. If your case is not so complex, use `to_snake_case`.

    Warning! Conversion is not reversible anymore.
    You cannot get "getHTTPResponse" from "get_http_response".
    """
    camel_str = SELECT_ABBREVIATIONS_PATTERN.sub(r"\1_\2", camel_str)
    return SEPARATE_WORD_FORM_ABBREVIATIONS_PATTERN.sub(r"\1_\2", camel_str).lower()


def dict_keys_to_snake_case_recursively(
    d: Dict[str, Any], snake_case_serializer: SnakeCaseEncoder = to_snake_case
) -> Dict[str, Any]:
    """
    Convert dictionary key names from `camelCase` to `snake_case`.
    Use `to_snake_case_safe` instead of usual `to_snake_case` if you have complex naming case.
    """
    return {
        snake_case_serializer(key): dict_keys_to_snake_case_recursively(value)
        if isinstance(value, dict)
        else value
        for key, value in d.items()
    }


def to_camel_case(snake_str: str) -> str:
    """
    Convert string from `snake_case` to `camelCase`
    """
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def dict_keys_to_camel_case_recursively(d: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert dictionary key names from `snake_case` to `camelCase`
    """
    return {
        to_camel_case(key): dict_keys_to_camel_case_recursively(value)
        if isinstance(value, dict)
        else value
        for key, value in d.items()
    }


def read_scheme_from_file(file_path: str, *, encoding: str = "UTF-8") -> str:
    """
    Read GraphQL scheme (actually not only GraphQL scheme but any data) from file
    """
    with open(file_path, "r+", encoding=encoding) as f:
        return f.read()


def get_dir_from_file_path(file_path: str) -> str:
    """
    Get folder name from file path
    """
    return path.dirname(path.realpath(file_path))
