"""GraphQL client, high performance, easy to use, sync/async support"""

__version__ = "0.3.1"

from .client import AsyncClient as AsyncClient
from .client import Client as Client
from .request import GraphQLRequest as GraphQLRequest
