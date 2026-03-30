import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from scipy.stats import norm
import os
from dotenv import load_dotenv
from python.stats.insight_generator import load_segment_data, analyze_segments, generate_insight
load_dotenv()

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

def load_data():
    query = "SELECT * FROM fct_experiment_metrics"
    return pd.read_sql(query, engine)


def compute_stats(df):
    control = df[df["variant"] == "control"].iloc[0]
    treatment = df[df["variant"] == "treatment"].iloc[0]

    p1 = control["conversion_rate"]
    p2 = treatment["conversion_rate"]

    n1 = control["users"]
    n2 = treatment["users"]

    # lift
    lift = (p2 - p1) / p1

    # standard error
    se = np.sqrt(
        (p1 * (1 - p1)) / n1 +
        (p2 * (1 - p2)) / n2
    )

    z = (p2 - p1) / se
    p_value = 2 * (1 - norm.cdf(abs(z)))

    return {
        "control_cr": p1,
        "treatment_cr": p2,
        "lift": lift,
        "p_value": p_value
    }


def decision_logic(stats):
    if stats["p_value"] < 0.05 and stats["lift"] > 0:
        return "SHIP"
    elif stats["p_value"] < 0.05 and stats["lift"] < 0:
        return "DO NOT SHIP"
    else:
        return "INCONCLUSIVE"


def main():
    # --- Stats ---
    df = load_data()
    stats = compute_stats(df)
    decision = decision_logic(stats)

    print("\n--- Experiment Results ---")
    print(f"Control CR: {stats['control_cr']:.4f}")
    print(f"Treatment CR: {stats['treatment_cr']:.4f}")
    print(f"Lift: {stats['lift']*100:.2f}%")
    print(f"P-value: {stats['p_value']:.5f}")
    print(f"Decision: {decision}")

    # --- Segment Insight ---
    segment_df = load_segment_data()
    analyzed = analyze_segments(segment_df)
    insight = generate_insight(analyzed)

    print("\n--- Segment Insight ---")
    print(insight)


if __name__ == "__main__":
    main()