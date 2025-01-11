# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["OrderBook"]


class OrderBook(BaseModel):
    asks: Optional[List[List[float]]] = None

    bids: Optional[List[List[float]]] = None
