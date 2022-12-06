from typing import Dict, List


class GraphQLError(Exception):
    """Base exception for GraphQL clients."""

    def __init__(self, errors: List[Dict]) -> None:
        message = "\n".join(
            error.get("message") or "\n".join(error.get("messages")) for error in errors
        )
        super().__init__(message)


class ClientAlreadyConnected(Exception):
    """
    Client tries to reconnect to a new session when the old session is not closed.
    """
