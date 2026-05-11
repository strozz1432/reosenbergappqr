"""Create demo school + users. Run from backend/: python seed.py"""

import secrets

from sqlalchemy import select

from app.db import SessionLocal, engine
from app.migrate import run_migrations
from app.models import School, User
from app.security import hash_password


def seed() -> None:
    run_migrations(engine)
    db = SessionLocal()
    try:
        school = db.scalar(select(School).order_by(School.id).limit(1))
        if school is None:
            school = School(name="Demo School", qr_secret=secrets.token_urlsafe(32))
            db.add(school)
            db.commit()
            db.refresh(school)

        demo_users = [
            ("admin", "admin123", "admin", "Demo Admin"),
            ("student1", "student123", "student", "Alice Student"),
            ("student2", "student456", "student", "Bob Student"),
        ]
        for username, password, role, full_name in demo_users:
            existing = db.scalar(
                select(User).where(User.username == username, User.school_id == school.id)
            )
            if existing:
                print(f"Skip existing user: {username}")
                continue
            db.add(
                User(
                    school_id=school.id,
                    username=username,
                    password_hash=hash_password(password),
                    role=role,
                    full_name=full_name,
                )
            )
            print(f"Created user: {username} ({role})")
        db.commit()
        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
