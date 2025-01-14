from datetime import datetime

from pydantic import BaseModel
from xync_schema.models import Fiat, Msg


class FiatUpd(BaseModel):
    detail: str | None = None
    name: str | None = None
    amount: float | None = None
    target: int | None = None


class FiatNew(FiatUpd):
    cur_id: int
    pm_id: int
    detail: str
    amount: float = 0


class OrderPyd(BaseModel):
    id: int
    amount: float
    status: str
    actions: dict | None = None
    fiat: Fiat.pyd()
    is_sell: bool
    contragent: int | None = None
    created_at: datetime
    payed_at: datetime | None = None
    appealed_at: datetime | None = None
    confirmed_at: datetime | None = None
    msgs: list[Msg.pyd()] = []
