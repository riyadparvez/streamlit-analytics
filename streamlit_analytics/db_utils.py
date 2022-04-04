from __future__ import annotations
from datetime import datetime
from sqlalchemy.dialects.sqlite import JSON
from sqlmodel import Column, Field, Session, SQLModel, create_engine, select
from typing import Any

from constants import *


class Analytics(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    start_timestamp: datetime
    end_timestamp: datetime
    session_values: dict[Any, Any] = Field(index=False, sa_column=Column(JSON))


class DbAdapter:
    def __init__(self, db_url: str | None):
        if db_url is None:
            db_url = "sqlite:///:memory:"

        self.db_url = db_url
        self.db_engine = create_engine(db_url)
        SQLModel.metadata.create_all(self.db_engine)

    def insert_row(self, session_analytics: dict[str, Any]) -> None:
        with Session(self.db_engine) as session:
            # Writing
            start_timestamp = session_analytics[namespace_key]["start_timestamp"]
            end_timestamp = session_analytics[namespace_key]["end_timestamp"]
            session_analytics[namespace_key]["start_timestamp"] = session_analytics[
                namespace_key
            ]["start_timestamp"].isoformat()
            session_analytics[namespace_key]["end_timestamp"] = session_analytics[
                namespace_key
            ]["end_timestamp"].isoformat()

            current_session = Analytics(
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                session_values=session_analytics,
            )
            session.add(current_session)
            session.commit()
