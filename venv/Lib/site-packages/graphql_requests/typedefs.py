from typing import Callable

JSONEncoder = Callable[..., str]

SnakeCaseEncoder = Callable[[str], str]
