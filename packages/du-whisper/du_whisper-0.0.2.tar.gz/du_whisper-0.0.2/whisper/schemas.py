# -*- coding: utf-8 -*-
# 数据结构
from pydantic import BaseModel


class InData(BaseModel):
    """接受数据格式"""
    data: bytes
    original: str = 'auto'  # 原始语言
    to: str | None = None  # 翻译语言


class OutData(BaseModel):
    """返回数据格式"""
    sid: str
    data: str
    transl: str | None = None
