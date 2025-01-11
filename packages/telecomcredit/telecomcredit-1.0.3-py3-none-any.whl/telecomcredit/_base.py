from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CommonModel(BaseModel):
    # 任意パラメータが可とのとこなので、Attributeの追加許可
    model_config = ConfigDict(extra="allow")

    clientip: str
    money: int
    sendid: str | None = None
