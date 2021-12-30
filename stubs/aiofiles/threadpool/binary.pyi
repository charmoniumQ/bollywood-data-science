from ..base import AsyncBase as AsyncBase
from .utils import (
    delegate_to_executor as delegate_to_executor,
    proxy_method_directly as proxy_method_directly,
    proxy_property_directly as proxy_property_directly,
)

class AsyncBufferedIOBase(AsyncBase): ...
class AsyncBufferedReader(AsyncBufferedIOBase): ...
class AsyncFileIO(AsyncBase): ...
