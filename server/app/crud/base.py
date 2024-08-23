from typing import Generic, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from server.app.db.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
GetSchemaType = TypeVar("GetSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(
            self,
            db: Session,
            id: any,
            *,
            options: list | None = None,
            return_schema: Type[GetSchemaType] | None = None
    ) -> ModelType | GetSchemaType | None:
        query = db.query(self.model)
        if options:
            query = query.options(*options)
        db_obj = query.filter(self.model.id == id).first()
        if return_schema and db_obj:
            return return_schema.model_validate(db_obj)
        return db_obj

    def get_multi(
            self,
            db: Session,
            *,
            skip: int = 0,
            limit: int = 100,
            return_schema: Type[GetSchemaType] | None = None
    ) -> list[ModelType] | list[GetSchemaType]:
        db_objs = db.query(self.model).offset(skip).limit(limit).all()
        if return_schema:
            return [return_schema.model_validate(obj) for obj in db_objs]
        return db_objs

    def create(
            self,
            db: Session,
            *,
            obj_in: CreateSchemaType,
            return_schema: Type[GetSchemaType] | None = None
    ) -> ModelType | GetSchemaType:
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        if return_schema:
            return return_schema.model_validate(db_obj)
        return db_obj

    def update(
            self,
            db: Session,
            *,
            db_obj: ModelType,
            obj_in: UpdateSchemaType | dict[str, any],
            return_schema: Type[GetSchemaType] | None = None
    ) -> ModelType | GetSchemaType:
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        if return_schema:
            return return_schema.model_validate(db_obj)
        return db_obj

    def remove(
            self,
            db: Session,
            *,
            id: int,
            return_schema: Type[GetSchemaType] | None = None
    ) -> ModelType | GetSchemaType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        if return_schema:
            return return_schema.model_validate(obj)
        return obj
