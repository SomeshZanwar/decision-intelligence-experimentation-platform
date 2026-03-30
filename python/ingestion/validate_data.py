from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

def run_checks():
    checks = {
        "users": "SELECT COUNT(*) FROM users",
        "assignments": "SELECT COUNT(*) FROM experiment_assignments",
        "events": "SELECT COUNT(*) FROM events",
        "orders": "SELECT COUNT(*) FROM orders"
    }

    with engine.connect() as conn:
        for name, query in checks.items():
            result = conn.execute(text(query)).fetchone()[0]
            print(f"{name}: {result}")

        # sanity check: every user assigned
        mismatch = conn.execute(text("""
            SELECT COUNT(*)
            FROM users u
            LEFT JOIN experiment_assignments ea
            ON u.user_id = ea.user_id
            WHERE ea.user_id IS NULL
        """)).fetchone()[0]

        print("Users without assignment:", mismatch)


if __name__ == "__main__":
    run_checks()