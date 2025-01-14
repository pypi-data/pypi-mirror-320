from typing import Optional
from typing_extensions import TypedDict

class SearchEndpointsRequest(TypedDict, total=False):
    """
    Request object for searching endpoints in the API
    """
    q: str # tool name
    q2: str # tool description
    limit: Optional[int]
    index_name: Optional[str]
