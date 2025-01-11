from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from requests import Response, post

from telecomcredit._base import CommonModel


class Order(CommonModel):
    usrtel: str | None = None
    usrmail: str | None = None
    sendpass: str | None = None
    send_pass_bool: str | None = None
    non_duplication_id: str | None = None
    redirect_url: str | None = None
    redirect_back_url: str | None = None
    option: str | None = None


def get_order_url(self, *, money: int, **kwargs: dict[str, Any]) -> str:
    """
    都度決済用URL取得
    :param self
    :param money: int: 金額
    :param kwargs: dict[str, Any]: その他
    :return: str: URL
    """
    model = Order(clientip=self._clientip, money=money, **kwargs)
    return f"{self._base_url}?{urlencode(model.model_dump(exclude_none=True))}"


def post_order(self, money: int, **kwargs: dict[str, Any]) -> Response:
    """
    都度決済用へ金額やその他指定して遷移
    :param self
    :param money: int: 金額
    :param kwargs: dict[str, Any]: その他
    :return: Response: POST結果
    """
    model = Order(clientip=self._clientip, money=money, **kwargs)
    return post(self._base_url, data=model.model_dump(exclude_none=True), timeout=10)
