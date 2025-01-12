'''
Descripttion: 
version: 0.x
Author: zhai
Date: 2025-01-11 23:03:47
LastEditors: zhai
LastEditTime: 2025-01-11 23:36:21
'''

from datetime import datetime
from sqlalchemy import UUID
from tortoise import Model, fields
from ._settings import CRUD_DATETIME_FORMAT


class CrudModel(Model):
    """Base for all models."""

    # id = fields.IntField(pk=True)
    id = fields.UUIDField(primary_key=True)
    creation_date = fields.DatetimeField(auto_now_add=True, description="创建时间")
    created_by = fields.IntField(null=True, description="创建人ID")
    updation_date = fields.DatetimeField(auto_now=True, description="更新时间")
    updated_by = fields.IntField(null=True, description="更新人ID")
    enabled_flag = fields.BooleanField(default=True, description="是否删除, 0 删除 1 非删除")
    trace_id = fields.CharField(max_length=255, null=True, description="trace_id")

    async def to_dict(
            self, include_fields: list[str] | None = None, exclude_fields: list[str] | None = None
    ):
        include_fields = include_fields or []
        exclude_fields = exclude_fields or []

        d = {}
        for field in self._meta.db_fields:
            if (not include_fields or field in include_fields) and (not exclude_fields or field not in exclude_fields):
                value = getattr(self, field)
                if isinstance(value, datetime):
                    value = value.strftime(CRUD_DATETIME_FORMAT)
                elif isinstance(value, UUID):
                    value = str(value)
                d[field] = value

        return d


    class Meta:
        abstract = True
        table_description = "Base model with common fields"
        table_args = {
            "charset": "utf8"
        }

    