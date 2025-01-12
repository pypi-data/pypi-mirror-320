from typing import List, Literal, Type, TypeVar, Union
from uuid import UUID
from pydantic import BaseModel
from tortoise import fields, Model

###########################################################################################
# Define a generic type variable
ModelType = TypeVar("ModelType", bound=Model)
PydanticType = TypeVar("PydanticType", bound=BaseModel)

def model_to_dict_no_relation(model: Model):
    # Get the fields of the model that are not relations
    non_relation_fields = {}
    for field_name, field in model._meta.fields_map.items():
        if not isinstance(
            field,
            (
                fields.relational.ForeignKeyFieldInstance,
                fields.relational.BackwardFKRelation,
                fields.relational.ManyToManyFieldInstance,
            ),
        ):
            value = getattr(model, field_name)
            non_relation_fields[field_name] = str(value) if isinstance(value, UUID) else value
    return non_relation_fields


def model_to_dict_relation(model, seen=None):
    if seen is None:
        seen = set()

    if model in seen:
        return None

    seen.add(model)

    result = {}

    # if field_name in model_class._meta.fetch_fields and issubclass(field_type, PydanticModel):
    #         subclass_fetch_fields = _get_fetch_fields(
    #             field_type, field_type.model_config["orig_model"]
    #         )
    #         if subclass_fetch_fields:
    #             fetch_fields.extend([field_name + "__" + f for f in subclass_fetch_fields])
    #         else:
    #             fetch_fields.append(field_name)
    # return fetch_fields

    for field_name, field in model._meta.fields_map.items():
        if isinstance(field, fields.relational.ForeignKeyFieldInstance):
            # await model.fetch_related(field_name)
            related = getattr(model, field_name)
            if related:
                result[field_name] = model_to_dict_no_relation(related)
        elif isinstance(
            field,
            (
                fields.relational.BackwardFKRelation,
                fields.relational.ManyToManyFieldInstance,
            ),
        ):
            # await model.fetch_related(field_name)
            related = getattr(model, field_name)
            if related:
                result[field_name] = [
                    model_to_dict_no_relation(item) for item in related.related_objects
                ]

                result[f"{field_name}_refids"] = [
                    getattr(item, "id") for item in related.related_objects
                ]
        else:
            result[field_name] = getattr(model, field_name)

    return result

    # await page.fetch_related('book')
    # book = page.book

    for relationship in model.__mapper__.relationships:
        try:
            related_obj = getattr(model, relationship.key)
        except Exception as e:
            result[relationship.key] = None
            continue

        if related_obj is None:
            result[relationship.key] = None
        else:
            if relationship.uselist:
                result[relationship.key] = [
                    model_to_dict_relation(item, seen) for item in related_obj
                ]
            else:
                result[relationship.key] = model_to_dict_relation(related_obj, seen)

    return result


def convert_to_pydantic(
    data: Union[dict, ModelType, List[ModelType]],
    pydantic_model: Type[PydanticType],
    relationships: bool = False,
    mode: Literal["json", "python"] | str = "python",
) -> Union[PydanticType, List[PydanticType]]:
    if data is None:
        return None
    elif isinstance(data, dict):
        return pydantic_model.model_validate(data).model_dump(mode=mode)
    elif isinstance(data, list):
        return [
            convert_to_pydantic(item, pydantic_model, relationships, mode)
            for item in data
        ]
    elif isinstance(data, Model):
        if relationships:
            return pydantic_model.model_validate(
                model_to_dict_relation(data),
            ).model_dump(mode=mode)
        else:
            return pydantic_model.model_validate(
                model_to_dict_no_relation(data),
            ).model_dump(mode=mode)
    else:
        raise ValueError("Invalid input data type")

