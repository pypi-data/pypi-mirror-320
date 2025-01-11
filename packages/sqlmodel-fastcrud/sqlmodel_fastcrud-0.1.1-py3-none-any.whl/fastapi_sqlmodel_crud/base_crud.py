from datetime import datetime, timezone
from typing import Generic, Type, TypeVar, List, Optional

from sqlmodel import Session, SQLModel, select

from .exceptions import NotFoundError, DatabaseError
from .base_filter import BaseFilter

TModel = TypeVar("TModel", bound=SQLModel)


class AbstractCRUD(Generic[TModel]):
    def __init__(self, model: Type[TModel], db_session: Session):
        self.model = model
        self.db_session = db_session

    def create(self, obj_data: TModel) -> TModel:
        """
        Create a new record.
        """
        try:
            if hasattr(obj_data, "created_at"):
                obj_data.created_at = datetime.now(timezone.utc)
            if hasattr(obj_data, "modified_at"):
                obj_data.modified_at = datetime.now(timezone.utc)

            self.db_session.add(obj_data)
            self.db_session.commit()
            self.db_session.refresh(obj_data)
            return obj_data
        except Exception as e:
            raise DatabaseError(f"Failed to create {self.model.__name__}: {e}")

    def get(self, id: int) -> TModel:
        """
        Retrieve a record by ID.
        """
        try:
            obj = self.db_session.get(self.model, id)
            if not obj:
                raise NotFoundError(f"{self.model.__name__} with ID '{id}' not found.")
            return obj
        except NotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve {self.model.__name__} with ID '{id}': {e}")

    def get_all(
        self, 
        filter_field: Optional[BaseFilter] = None, 
        sort_field: Optional[str] = None, 
        ascending: bool = True, 
        skip: int = 0, 
        limit: int = 10
    ) -> List[TModel]:
        """
        Retrieve records based on filters, sorting, and pagination.
        """
        try:
            query = select(self.model)
            if filter_field:
                filter_field.model = self.model
                query = filter_field.filter(query)
                query = filter_field.sort(query, sort_field, ascending)
            
            query = query.offset(skip).limit(limit)
            return self.db_session.exec(query).all()
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve {self.model.__name__} records: {e}")

    def update(self, id: int, obj_data: TModel) -> TModel:
        """
        Update an existing record by ID.
        """
        try:
            obj = self.db_session.get(self.model, id)
            if not obj:
                raise NotFoundError(f"{self.model.__name__} with ID '{id}' not found.")

            update_data = obj_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(obj, key, value)

            if hasattr(obj, "modified_at"):
                obj.modified_at = datetime.now(timezone.utc)

            self.db_session.commit()
            self.db_session.refresh(obj)
            return obj
        except NotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to update {self.model.__name__} with ID '{id}': {e}")

    def delete(self, id: int) -> bool:
        """
        Delete a record by ID.
        """
        try:
            obj = self.db_session.get(self.model, id)
            if not obj:
                raise NotFoundError(f"{self.model.__name__} with ID '{id}' not found.")

            self.db_session.delete(obj)
            self.db_session.commit()
            return True
        except NotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to delete {self.model.__name__} with ID '{id}': {e}")
