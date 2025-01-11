from __future__ import annotations

from enum import Enum
from telecomcredit._base import CommonModel
from typing import Any, Literal
from uuid import UUID


class RelEnum(Enum):
    YES = "yes"
    NO = "no"


class ContEnum(Enum):
    YES = "yes"
    NO = "no"


class Result(CommonModel):
    telno: str
    email: str
    username: str | None = None
    sendpass: str | None = None
    rel: RelEnum
    cont: ContEnum
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
