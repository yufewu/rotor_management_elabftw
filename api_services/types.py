"""Type definitions for eLabFTW API responses."""

from typing import Protocol, Any, runtime_checkable


@runtime_checkable
class ApiResponse(Protocol):
    """Protocol defining the structure of an eLabFTW API response.
    
    This ensures that any API response object has the required attributes
    and helps type checkers understand the available methods and attributes.
    """
    
    data: Any  # Raw response data (typically bytes)
    headers: Any  # Response headers (typically dict)
