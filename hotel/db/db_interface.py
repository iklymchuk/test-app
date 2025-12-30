from typing import Any, List, Optional
from sqlalchemy.orm import Session

from hotel.db import engine
from hotel.db.models import Base, to_dict


DataObject = dict[str, Any]


class DBInterface:
    def __init__(self, db_class: type[Base], session: Optional[Session] = None):
        """
        Initialize DBInterface with a model class and optional session.

        Args:
            db_class: SQLAlchemy model class to work with
            session: Optional SQLAlchemy session. If None, uses production DBSession
        """
        self.db_class = db_class
        self._session = session  # Store session for testing

    def _get_session(self) -> Session:
        """Get session - either test session or production session."""
        if self._session is not None:
            return self._session
        return engine.DBSession()

    def read_by_id(self, id: int) -> DataObject:
        session = self._get_session()
        result = session.get(self.db_class, id)
        return to_dict(result)

    def read_all(self) -> List[DataObject]:
        session = self._get_session()
        results = session.query(self.db_class).all()
        return [to_dict(result) for result in results]

    def create(self, data: DataObject) -> DataObject:
        session = self._get_session()
        result = self.db_class(**data)
        session.add(result)
        session.commit()
        return to_dict(result)

    def update(self, id: int, data: DataObject) -> DataObject:
        session = self._get_session()
        result = session.get(self.db_class, id)
        if not result:
            return None
        # Only update fields that are not None (partial updates)
        for key, value in data.items():
            if value is not None:
                setattr(result, key, value)
        session.commit()
        return to_dict(result)

    def delete(self, id: int) -> DataObject:
        session = self._get_session()
        result = session.get(self.db_class, id)
        session.delete(result)
        session.commit()
        return to_dict(result)
