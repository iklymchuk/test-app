from typing import Any, List

from hotel.db import engine
from hotel.db.models import Base, to_dict


DataObject = dict[str, Any]


class DBInterface:
    def __init__(self, db_class: type[Base]):
        self.db_class = db_class    # Store which model to work with

    def read_by_id(self, id: int) -> DataObject:
        session = engine.DBSession()
        result = session.query(self.db_class).get(id)
        return to_dict(result)

    def read_all(self) -> List[DataObject]:
        session = engine.DBSession()
        results = session.query(self.db_class).all()
        return [to_dict(result) for result in results]

    def create(self, data: DataObject) -> DataObject:
        session = engine.DBSession()
        result = self.db_class(**data)
        session.add(result)
        session.commit()
        return to_dict(result)

    def update(self, id: int, data: DataObject) -> DataObject:
        session = engine.DBSession()
        result = session.query(self.db_class).get(id)
        if not result:
            return None
        for key, value in data.items():
            setattr(result, key, value)
        session.commit()
        return to_dict(result)

    def delete(self, id: int) -> DataObject:
        session = engine.DBSession()
        result = session.query(self.db_class).get(id)
        session.delete(result)
        session.commit()
        return to_dict(result)
