"""Lightweight SQLite-friendly adjustments when models gain new columns."""

import secrets

from sqlalchemy import inspect, select, text, update
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Base, School, User


def run_migrations(engine) -> None:
    Base.metadata.create_all(bind=engine)
    insp = inspect(engine)

    if "users" in insp.get_table_names():
        cols = {c["name"] for c in insp.get_columns("users")}
        if "school_id" not in cols:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN school_id INTEGER"))

    db: Session = SessionLocal()
    try:
        school = db.scalar(select(School).order_by(School.id).limit(1))
        if school is None:
            school = School(
                name="Demo School",
                qr_secret=secrets.token_urlsafe(32),
            )
            db.add(school)
            db.commit()
            db.refresh(school)

        db.execute(update(User).where(User.school_id.is_(None)).values(school_id=school.id))
        db.commit()
    finally:
        db.close()
