from __future__ import annotations

from typing import Any
from uuid import UUID

from telecomcredit._base import CommonModel


class Result(CommonModel):
    telno: str
    email: str
    username: str | None = None
    sendpass: str | None = None
    rel: str
    cont: str
    settle_uuid: UUID
    option: str | None = None
    rebill_param_id: str | None = None


def received_result(self, **kwargs: dict[str, Any]) -> Result:  # noqa: ARG001
    """
    結果取得用Webhook
    TELECOMCREDITから送られてくるGET/POSTの中身をkwargsとして受け渡す
    :param self
    :param kwargs: dict[str, Any]: GET/POSTの中身
    :return: Result: TELECOMCREDITからの結果
    """
    return Result(**kwargs)
