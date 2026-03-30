import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv




load_dotenv(dotenv_path=".env")

random.seed(42)
np.random.seed(42)

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Somesh@2701")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "experiment_db")

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

EXPERIMENT_START = datetime(2026, 1, 1)
EXPERIMENT_END = datetime(2026, 1, 14)
N_USERS = 50000

COUNTRIES = ["US", "India", "UK", "Canada"]
COUNTRY_PROBS = [0.50, 0.20, 0.15, 0.15]

PLATFORMS = ["iOS", "Android", "Web"]
PLATFORM_PROBS = [0.35, 0.40, 0.25]


def random_date(start, end):
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def generate_experiment():
    return pd.DataFrame(
        [{
            "name": "checkout_redesign_experiment",
            "hypothesis": "The redesigned checkout flow will increase conversion rate without reducing average order value or retention.",
            "start_date": EXPERIMENT_START.date(),
            "end_date": EXPERIMENT_END.date(),
            "status": "completed"
        }]
    )


def generate_users(n_users):
    user_ids = np.arange(1, n_users + 1)
    signup_dates = [
        (EXPERIMENT_START - timedelta(days=random.randint(1, 365))).date()
        for _ in range(n_users)
    ]
    countries = np.random.choice(COUNTRIES, size=n_users, p=COUNTRY_PROBS)
    platforms = np.random.choice(PLATFORMS, size=n_users, p=PLATFORM_PROBS)
    is_active = np.random.choice([True, False], size=n_users, p=[0.92, 0.08])

    return pd.DataFrame({
        "user_id": user_ids,
        "signup_date": signup_dates,
        "country": countries,
        "platform": platforms,
        "is_active": is_active
    })


def assign_variants(users_df, experiment_id=1):
    variants = np.random.choice(["control", "treatment"], size=len(users_df), p=[0.5, 0.5])
    assigned_at = [random_date(EXPERIMENT_START, EXPERIMENT_START + timedelta(days=1)) for _ in range(len(users_df))]

    return pd.DataFrame({
        "experiment_id": experiment_id,
        "user_id": users_df["user_id"],
        "variant": variants,
        "assigned_at": assigned_at
    })


def get_conversion_probability(platform, country, variant):
    base = 0.08

    if platform == "iOS" and country == "US":
        base += 0.015
    elif platform == "Web":
        base += 0.005

    if variant == "treatment":
        if platform == "iOS" and country == "US":
            base += 0.020
        elif platform == "Web":
            base += 0.010
        elif platform == "Android":
            base += 0.002
        else:
            base += 0.005

    return min(base, 0.20)


def generate_sessions_and_events(users_df, assignments_df):
    sessions = []
    events = []
    orders = []
    session_counter = 1

    user_lookup = users_df.set_index("user_id").to_dict("index")
    assignment_lookup = assignments_df.set_index("user_id").to_dict("index")

    for user_id in users_df["user_id"]:
        profile = user_lookup[user_id]
        variant = assignment_lookup[user_id]["variant"]

        n_sessions = random.randint(1, 5)
        converted = False

        for _ in range(n_sessions):
            session_id = f"sess_{session_counter}"
            session_counter += 1

            session_start = random_date(EXPERIMENT_START, EXPERIMENT_END)
            session_end = session_start + timedelta(minutes=random.randint(2, 45))

            sessions.append({
                "session_id": session_id,
                "user_id": user_id,
                "session_start": session_start,
                "session_end": session_end
            })

            funnel_events = ["view_product"]

            if random.random() < 0.55:
                funnel_events.append("add_to_cart")
            if random.random() < 0.30:
                funnel_events.append("checkout_start")

            conv_prob = get_conversion_probability(profile["platform"], profile["country"], variant)

            if (not converted) and ("checkout_start" in funnel_events) and (random.random() < conv_prob):
                funnel_events.append("purchase")
                converted = True

                order_value = np.random.normal(82 if variant == "control" else 80, 20)
                order_value = max(10, round(order_value, 2))

                orders.append({
                    "user_id": user_id,
                    "order_value": order_value,
                    "order_timestamp": session_end,
                    "experiment_id": 1,
                    "variant": variant
                })

            for event_name in funnel_events:
                event_ts = session_start + timedelta(seconds=random.randint(0, int((session_end - session_start).total_seconds())))
                events.append({
                    "user_id": user_id,
                    "event_type": event_name,
                    "event_timestamp": event_ts,
                    "session_id": session_id
                })

    return pd.DataFrame(sessions), pd.DataFrame(events), pd.DataFrame(orders)


def main():
    experiment_df = generate_experiment()
    users_df = generate_users(N_USERS)
    assignments_df = assign_variants(users_df, experiment_id=1)
    sessions_df, events_df, orders_df = generate_sessions_and_events(users_df, assignments_df)

    os.makedirs("data/raw", exist_ok=True)

    experiment_df.to_csv("data/raw/experiments.csv", index=False)
    users_df.to_csv("data/raw/users.csv", index=False)
    assignments_df.to_csv("data/raw/assignments.csv", index=False)
    sessions_df.to_csv("data/raw/sessions.csv", index=False)
    events_df.to_csv("data/raw/events.csv", index=False)
    orders_df.to_csv("data/raw/orders.csv", index=False)

    print("Generated:")
    print(f"Users: {len(users_df):,}")
    print(f"Assignments: {len(assignments_df):,}")
    print(f"Sessions: {len(sessions_df):,}")
    print(f"Events: {len(events_df):,}")
    print(f"Orders: {len(orders_df):,}")

    experiment_df.to_sql("experiments", engine, if_exists="append", index=False)
    users_df.to_sql("users", engine, if_exists="append", index=False)
    assignments_df.to_sql("experiment_assignments", engine, if_exists="append", index=False)
    sessions_df.to_sql("sessions", engine, if_exists="append", index=False)
    events_df.to_sql("events", engine, if_exists="append", index=False)
    orders_df.to_sql("orders", engine, if_exists="append", index=False)

    print("Data loaded into PostgreSQL.")


if __name__ == "__main__":
    main()