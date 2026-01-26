from typing import Generic, TypeVar, Type, Iterable
from sqlalchemy.orm import Session

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def get(self, id_: object) -> T | None:
        return self.db.get(self.model, id_)

    def add(self, entity: T) -> T:
        self.db.add(entity)
        return entity

    def add_all(self, entities: Iterable[T]) -> list[T]:
        entities = list(entities)
        self.db.add_all(entities)
        return entities

    def delete(self, entity: T) -> None:
        self.db.delete(entity)

    def list(self, limit: int = 100, offset: int = 0) -> list[T]:
        return (
            self.db.query(self.model)
            .offset(offset)
            .limit(limit)
            .all()
        )