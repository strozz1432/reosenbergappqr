"""Create demo admin + 2 students. Run from backend/: python seed.py"""

from sqlalchemy import select

from app.db import Base, SessionLocal, engine
from app.models import User  # noqa: F401 — registers metadata with Base
from app.security import hash_password


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        demo_users = [
            ("admin", "admin123", "admin", "Demo Admin"),
            ("student1", "student123", "student", "Alice Student"),
            ("student2", "student456", "student", "Bob Student"),
        ]
        for username, password, role, full_name in demo_users:
            existing = db.scalar(select(User).where(User.username == username))
            if existing:
                print(f"Skip existing user: {username}")
                continue
            db.add(
                User(
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
