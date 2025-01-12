from datetime import datetime
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Tuple,
    Type,
    TypeVar,
    cast,
    Coroutine,
    Optional,
    Union,
)

from fastapi import Depends, HTTPException, Request, Query
from fastapi.responses import ORJSONResponse
from fastapi.types import IncEx
from pydantic import BaseModel

from ._files import get_form_data, savefile, UploadFileType
from ._tortoise_convert import convert_to_pydantic

from ._base import CRUDGenerator, NOT_FOUND
from ._types import (
    DEPENDENCIES,
    PAGINATION,
    PYDANTIC_SCHEMA as SCHEMA,
    RespModelT,
    UserDataOption,
    UserDataFilter,
    UserDataFilterAll,
    UserDataFilterSelf,
    InvalidQueryException,
    IdNotExist,
)
from ._utils import get_pk_type, resp_success

from tortoise.models import Model
from tortoise.queryset import QuerySet
from tortoise import fields, transactions
from tortoise.expressions import Q

CALLABLE = Callable[..., Coroutine[Any, Any, Model]]
CALLABLE_LIST = Callable[..., Coroutine[Any, Any, List[Model]]]

# Mapping of operators to SQL operators
operator_mapping = {
    "=": "",
    "!=": "__not",
    ">": "__gt",
    "<": "__lt",
    ">=": "__gte",
    "<=": "__lte",
    "like": "__contains",
    "in": "__in",
}


def parse_query(
    query: List[
        Tuple[str, str, Union[str, int, float, datetime, List[Union[str, int, float]]]]
    ],
    queryset: QuerySet,
) -> QuerySet:
    filter_conditions = Q()

    for condition in query:
        if len(condition) != 3:
            raise InvalidQueryException(
                "Each condition must have exactly 3 elements: field, operator, and value."
            )

        field, operator, value = condition

        if operator not in operator_mapping:
            raise InvalidQueryException(f"Invalid operator: {operator}")

        # Construct the field name with the appropriate operator suffix
        field_with_operator = f"{field}{operator_mapping[operator]}"

        # Add the condition to the Q object
        filter_conditions &= Q(**{field_with_operator: value})

    return queryset.filter(filter_conditions)


class TortoiseCRUDRouter(CRUDGenerator[SCHEMA]):
    def __init__(
        self,
        schema: Type[SCHEMA],
        db_model: Type[Model],
        create_schema: Optional[Type[SCHEMA]] = None,
        update_schema: Optional[Type[SCHEMA]] = None,
        filter_schema: Optional[Type[SCHEMA]] = None,
        user_data_option: UserDataOption = UserDataOption.ALL_ONLY,
        prefix: Optional[str] = None,
        tags: Optional[List[str]] = None,
        paginate: Optional[int] = None,
        get_all_route: Union[bool, DEPENDENCIES] = True,
        get_one_route: Union[bool, DEPENDENCIES] = True,
        create_route: Union[bool, DEPENDENCIES] = True,
        update_route: Union[bool, DEPENDENCIES] = True,
        delete_one_route: Union[bool, DEPENDENCIES] = True,
        delete_all_route: Union[bool, DEPENDENCIES] = True,
        kcreate_route: Union[bool, DEPENDENCIES] = True,
        kbatch_create_route: Union[bool, DEPENDENCIES] = True,
        kdelete_route: Union[bool, DEPENDENCIES] = True,
        kdelete_all_route: Union[bool, DEPENDENCIES] = True,
        kupdate_route: Union[bool, DEPENDENCIES] = True,
        kget_by_id_route: Union[bool, DEPENDENCIES] = True,
        kget_one_by_filter_route: Union[bool, DEPENDENCIES] = True,
        klist_route: Union[bool, DEPENDENCIES] = True,
        kquery_route: Union[bool, DEPENDENCIES] = True,
        kquery_ex_route: Union[bool, DEPENDENCIES] = True,
        kupsert_route: Union[bool, DEPENDENCIES] = True,
        **kwargs: Any,
    ) -> None:
        # assert (
        #     tortoise_installed
        # ), "Tortoise ORM must be installed to use the TortoiseCRUDRouter."

        self.db_model = db_model
        self._pk: str = db_model.describe()["pk_field"]["db_column"]
        self._pk_type: type = get_pk_type(schema, self._pk)

        super().__init__(
            schema=schema,
            create_schema=create_schema,
            update_schema=update_schema,
            filter_schema=filter_schema,
            user_data_option=user_data_option,
            prefix=prefix or db_model.describe()["name"].replace("None.", ""),
            tags=tags,
            paginate=paginate,
            get_all_route=get_all_route,
            get_one_route=get_one_route,
            create_route=create_route,
            update_route=update_route,
            delete_one_route=delete_one_route,
            delete_all_route=delete_all_route,
            kcreate_route=kcreate_route,
            kbatch_create_route=kbatch_create_route,
            kdelete_route=kdelete_route,
            kdelete_all_route=kdelete_all_route,
            kupdate_route=kupdate_route,
            kget_by_id_route=kget_by_id_route,
            kget_one_by_filter_route=kget_one_by_filter_route,
            klist_route=klist_route,
            kquery_route=kquery_route,
            kquery_ex_route=kquery_ex_route,
            kupsert_route=kupsert_route,
            **kwargs,
        )

    def _get_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        async def route(pagination: PAGINATION = self.pagination) -> List[Model]:
            skip, limit = pagination.get("skip"), pagination.get("limit")

            query = self.db_model.all()
            total = await query.count()

            query = query.offset(cast(int, skip))
            if limit:
                query = query.limit(limit)
            objs = await query

            return resp_success(convert_to_pydantic(objs, self.schema), total=total)

        return route

    def _get_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(item_id: str) -> Model:
            try:
                obj = await self.db_model.get(**{self._pk: item_id})
                return resp_success(convert_to_pydantic(obj, self.schema))
            except Exception as e:
                raise NOT_FOUND

        return route

    def _create(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(model: self.create_schema, request: Request) -> Model:  # type: ignore
            obj = await self.__create_obj_with_model(model, request, exclude={self._pk})
            return resp_success(convert_to_pydantic(obj, self.schema))

        return route

    def _update(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: str, model: self.update_schema  # type: ignore
        ) -> Model:
            await self.db_model.filter(id=item_id).update(
                **model.dict(exclude_unset=True)
            )
            return await self._get_one()(item_id)

        return route

    def _delete_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        async def route() -> List[Model]:
            await self.db_model.all().delete()
            return await self._get_all()(pagination={"skip": 0, "limit": None})

        return route

    def _delete_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(item_id: str) -> Model:
            ret = await self.db_model.filter(id=item_id).delete()
            return resp_success(bool(ret))

        return route

    #################################################################################
    def _kcreate(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            model: self.create_schema,  # type: ignore
            request: Request,
        ) -> RespModelT[Optional[self.schema]]:
            obj = await self.__create_obj_with_model(model, request, exclude={self._pk})
            return resp_success(convert_to_pydantic(obj, self.schema))

        return route

    def _kbatch_create(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            models: List[self.create_schema],  # type: ignore
            request: Request,
        ) -> RespModelT[Optional[List[self.schema]]]:
            objs = []
            for model in models:
                obj = await self.__create_obj_with_model(
                    model, request, exclude={self._pk}
                )
                if obj:
                    objs.append(obj)
            return resp_success(convert_to_pydantic(objs, self.schema))

        return route

    def _kdelete_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self._pk_type,
            _hard: bool = True,
        ) -> RespModelT[Optional[bool]]:
            if _hard is False:
                ret = await self.db_model.filter(
                    **{self._pk: item_id, "enabled_flag": 1}
                ).update(enabled_flag=0)
            else:
                ret = await self.db_model.filter(**{self._pk: item_id}).delete()

            return resp_success(bool(ret))

        return route

    def _kdelete_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        async def route(
            _hard: bool = True,
        ) -> RespModelT[Optional[int]]:
            if _hard is False:
                ret = await self.db_model.filter(enabled_flag=1).update(enabled_flag=0)
            else:
                ret = await self.db_model.all().delete()

            return resp_success(bool(ret))

        return route

    def _kupdate(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            model: self.schema,
            request: Request,
        ) -> RespModelT[Optional[self.schema]]:
            try:
                obj = await self.db_model.get(**{self._pk: getattr(model, self._pk)})
                await self.__update_obj_with_model(obj, model, request)
                return resp_success(convert_to_pydantic(obj, self.schema))
            except Exception as e:
                raise ValueError("id不存在!")

        return route

    # 筛选
    def _kget_one_by_filter(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            filter: self.filter_schema,  # type: ignore
            request: Request,
            relationships: bool = False,
            user_data_filter: self.user_data_filter_type = self.user_data_filter_defv,
        ) -> RespModelT[Optional[self.schema]]:
            filter_dict = filter.model_dump(exclude_none=True)

            query = self.db_model.filter(enabled_flag=True)

            if (
                user_data_filter == UserDataFilter.SELF_DATA
                or user_data_filter == UserDataFilterSelf.SELF_DATA
            ):
                if hasattr(request.state, "user_id"):
                    query = query.filter(created_by=request.state.user_id)

            if filter_dict:
                query = query.filter(**filter_dict)

            if relationships:
                query = self.__autoload_options(query)

            obj = await query.first()

            # if relationships:
            #     await obj.fetch_related(self.db_model._meta.fetch_fields)

            if obj:
                return resp_success(
                    convert_to_pydantic(obj, self.schema, relationships)
                )
            else:
                raise NOT_FOUND

        return route

    # 自动加载选项函数
    def __autoload_options(self, query: QuerySet) -> QuerySet:
        return query.prefetch_related(*self.db_model._meta.fetch_fields)

    # list
    def _klist(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            request: Request,
            pagination: PAGINATION = self.pagination,
            sort_by: str = Query(None, description="Sort records by this field"),
            relationships: bool = False,
            user_data_filter: self.user_data_filter_type = self.user_data_filter_defv,
        ) -> RespModelT[Optional[List[self.schema]]]:
            skip, limit = pagination.get("skip"), pagination.get("limit")

            query = self.db_model.filter(enabled_flag=True)

            if (
                user_data_filter == UserDataFilter.SELF_DATA
                or user_data_filter == UserDataFilterSelf.SELF_DATA
            ):
                if hasattr(request.state, "user_id"):
                    query = query.filter(created_by=request.state.user_id)

            total = await query.count()

            if sort_by:
                query = query.order_by(sort_by)

            if skip:
                query = query.offset(cast(int, skip))

            if limit:
                query = query.limit(limit)

            if relationships:
                query = self.__autoload_options(query)

            objs = await query

            # if relationships:
            #     await objs.fetch_related(self.db_model._meta.fetch_fields)

            current = None
            size = None
            if skip and limit:
                size = limit
                current = skip // limit + 1

            return resp_success(
                convert_to_pydantic(objs, self.schema, relationships),
                total,
                current,
                size,
            )

        return route

    # 筛选
    def _kquery(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            filter: self.filter_schema,  # type: ignore
            request: Request,
            pagination: PAGINATION = self.pagination,
            sort_by: str = Query(None, description="Sort records by this field"),
            relationships: bool = False,
            user_data_filter: self.user_data_filter_type = self.user_data_filter_defv,
        ) -> RespModelT[Optional[List[self.schema]]]:
            filter_dict = filter.model_dump(exclude_none=True)

            skip, limit = pagination.get("skip"), pagination.get("limit")

            query = self.db_model.filter(enabled_flag=True)

            if (
                user_data_filter == UserDataFilter.SELF_DATA
                or user_data_filter == UserDataFilterSelf.SELF_DATA
            ):
                if hasattr(request.state, "user_id"):
                    query = query.filter(created_by=request.state.user_id)

            if filter_dict:
                query = query.filter(**filter_dict)

            total = await query.count()

            if sort_by:
                query = query.order_by(sort_by)

            if skip:
                query = query.offset(cast(int, skip))

            if limit:
                query = query.limit(limit)

            if relationships:
                query = self.__autoload_options(query)

            objs = await query

            # if relationships:
            #     await objs.fetch_related(self.db_model._meta.fetch_fields)

            current = None
            size = None
            if skip and limit:
                size = limit
                current = skip // limit + 1

            return resp_success(
                convert_to_pydantic(objs, self.schema, relationships),
                total,
                current,
                size,
            )

        return route

    # 筛选
    # Example query: [["age", ">=", 25], ["name", "=", "Alice"]]
    def _kquery_ex(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            query: List[Tuple[str, str, Union[str, int, float, datetime, List[Any]]]],
            request: Request,
            pagination: PAGINATION = self.pagination,
            sort_by: str = Query(None, description="Sort records by this field"),
            relationships: bool = False,
            user_data_filter: self.user_data_filter_type = self.user_data_filter_defv,
        ) -> RespModelT[Optional[List[self.schema]]]:
            skip, limit = pagination.get("skip"), pagination.get("limit")

            try:
                sql_query = self.db_model.filter(enabled_flag=True)

                if (
                    user_data_filter == UserDataFilter.SELF_DATA
                    or user_data_filter == UserDataFilterSelf.SELF_DATA
                ):
                    if hasattr(request.state, "user_id"):
                        sql_query = sql_query.filter(created_by=request.state.user_id)

                if query:
                    sql_query = parse_query(query, sql_query)

                if sort_by:
                    sql_query = sql_query.order_by(sort_by)

                total = await sql_query.count()

                if skip:
                    sql_query = sql_query.offset(cast(int, skip))

                if limit:
                    sql_query = sql_query.limit(limit)

                if relationships:
                    sql_query = self.__autoload_options(sql_query)

                objs = await sql_query

                # if relationships:
                #     await objs.fetch_related(self.db_model._meta.fetch_fields)

                current = None
                size = None
                if skip and limit:
                    size = limit
                    current = skip // limit + 1

                return resp_success(
                    convert_to_pydantic(objs, self.schema, relationships),
                    total,
                    current,
                    size,
                )

            except Exception:
                raise HTTPException(
                    status_code=400, detail="Invalid query format or sort_by field"
                )

        return route

    # 插入冲突则更新
    def _kupsert(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            model: self.schema,  # type: ignore
            request: Request,
        ) -> RespModelT[Optional[self.schema]]:
            if hasattr(model, self._pk):
                item_id = getattr(model, self._pk)
                # obj = await self.db_model.get(**{self._pk: item_id})
                obj = await self.db_model.filter(**{self._pk: item_id}).first()
                if obj:
                    await self.__update_obj_with_model(obj, model, request)
                    return resp_success(
                        convert_to_pydantic(obj, self.schema), msg="update"
                    )

            obj = await self.__create_obj_with_model(model, request, exclude=None)
            return resp_success(convert_to_pydantic(obj, self.schema), msg="created")

            # model_dict = model.model_dump(exclude={self._pk}, exclude_none=True)
            # params = await self.handle_data(model_dict, True, request)
            # obj, created = await self.db_model.update_or_create( **{self._pk: item_id}, defaults=params )

        return route
    
    def _kupload_file(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            request: Request,
            form_data: Dict[str, Any] = Depends(get_form_data)
        ) -> RespModelT[Optional[self.schema]]:
            fields = {}
            # 处理表单数据，区分文件字段和非文件字段
            for key, value in form_data.items():
                if isinstance(value, list):
                    fields[key] = []
                    for item in value:
                        if isinstance(item, UploadFileType):
                            stored_filename = savefile(item)
                            fields[key].append(stored_filename)
                        else:
                            fields[key].append(item)
                else:
                    if isinstance(value, UploadFileType):
                        stored_filename = savefile(value)
                        fields[key] = stored_filename
                    else:
                        fields[key] = value

            model = self.create_schema(**fields)
            obj = await self.__create_obj_with_model(model, request, exclude={self._pk})
            return resp_success(convert_to_pydantic(obj, self.schema))
        
        return route


    def _kupdate_file(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            request: Request,
            form_data: Dict[str, Any] = Depends(get_form_data)
        ) -> RespModelT[Optional[self.schema]]:
            fields = {}
            # 处理表单数据，区分文件字段和非文件字段
            for key, value in form_data.items():
                if isinstance(value, list):
                    fields[key] = []
                    for item in value:
                        if isinstance(item, UploadFileType):
                            stored_filename = savefile(item)
                            fields[key].append(stored_filename)
                        else:
                            fields[key].append(item)
                else:
                    if isinstance(value, UploadFileType):
                        stored_filename = savefile(value)
                        fields[key] = stored_filename
                    else:
                        fields[key] = value

            model = self.schema(**fields)
            
            try:
                obj = await self.db_model.get(**{self._pk: getattr(model, self._pk)})
                await self.__update_obj_with_model(obj, model, request)
                return resp_success(convert_to_pydantic(obj, self.schema))
            except Exception as e:
                raise ValueError("id不存在!")
        
        return route

    async def __create_obj_with_model(
        self, model, request: Request, exclude: IncEx = None
    ):
        model_dict = model.model_dump(exclude=exclude, exclude_none=True)
        params = await self.__handle_data(model_dict, True, request)
        obj = self.db_model(**params)
        await obj.save()
        return obj

    async def __update_obj_with_model(self, obj, model, request: Request):
        # 去掉关联对象
        model_dict = model.model_dump(
            exclude={self._pk, *self.db_model._meta.fetch_fields}, exclude_none=True
        )

        ##########################################################################################
        # Relationships
        relation_field = {
            key[:-7]: value
            for key, value in model_dict.items()
            if (value and key.endswith("_refids") and hasattr(self.db_model, key[:-7]))
        }

        obj_id = getattr(obj, self._pk)
        for rkey, rlist in relation_field.items():
            related_field = self.db_model._meta.fields_map[rkey]
            rclass = related_field.related_model

            try:
                if isinstance(related_field, fields.relational.BackwardFKRelation):
                    rfield = related_field.relation_field
                    update_val = {rfield: obj_id}
                    none_val = {rfield: None}

                    # 使用事务进行批量更新
                    async with transactions.in_transaction():
                        # 1. 删掉所有指向obj_id的外键引用
                        await rclass.filter(**update_val).update(**none_val)
                        # 2. 更新关联数据的外键
                        rpk: str = rclass._meta.pk_attr
                        filter_conditions = Q(**{f"{rpk}__in": rlist})
                        await rclass.filter(filter_conditions).update(**update_val)
                elif isinstance(related_field, fields.relational.ManyToManyFieldInstance):
                    rfield = related_field.model_field_name
                    await obj.fetch_related(rfield)
                    obj_related = getattr(obj, rfield)
                    await obj_related.clear()
                    filter_conditions = Q(**{f"{self._pk}__in": rlist})
                    robjs = await rclass.filter(filter_conditions)
                    for robj in robjs:
                        await obj_related.add(robj)
                else:
                    pass
            except Exception as e:
                print(e)

        ##########################################################################################

        params = await self.__handle_data(model_dict, False, request)

        # Update the fields with provided data
        for key, value in params.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        # Save the updated model instance
        await obj.save()

    async def __handle_data(
        self, data: Union[dict, list], create: bool, request: Request
    ) -> Union[dict, list]:
        """
        :param params: 参数列表
        :return: 过滤好的参数
        """
        if isinstance(data, dict):
            # 1. 只保留数据库字段
            # 2. 筛选掉的特定键列表

            db_model_fields = self.db_model._meta.fields_map.keys()

            keys_to_remove = ["creation_date", "updation_date", "enabled_flag"]
            params = {
                key: value
                for key, value in data.items()
                if ((key in db_model_fields) and (key not in keys_to_remove))
            }

            # 添加属性
            params["trace_id"] = getattr(request.state, "trace_id", 0)

            # User Info
            user_id = getattr(request.state, "user_id", 0)

            # if not params.get(self._pk, None):
            #     params["created_by"] = user_id

            if create:
                params["created_by"] = user_id

            params["updated_by"] = user_id

            return params

        if isinstance(data, list):
            params = [await self.__handle_data(item, create, request) for item in data]
            return params

        return data
