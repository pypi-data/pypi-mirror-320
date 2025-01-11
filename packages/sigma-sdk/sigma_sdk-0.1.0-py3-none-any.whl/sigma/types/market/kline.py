# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["Kline"]


class Kline(BaseModel):
    close: Optional[float] = None

    high: Optional[float] = None

    low: Optional[float] = None

    open: Optional[float] = None

    open_time: Optional[datetime] = FieldInfo(alias="openTime", default=None)

    volume: Optional[float] = None
