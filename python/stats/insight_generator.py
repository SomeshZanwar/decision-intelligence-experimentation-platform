import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

def load_segment_data():
    query = "SELECT * FROM fct_experiment_segments"
    return pd.read_sql(query, engine)


def analyze_segments(df):
    results = []

    grouped = df.groupby(["platform", "country"])

    for (platform, country), group in grouped:
        if len(group) < 2:
            continue

        control = group[group["variant"] == "control"]
        treatment = group[group["variant"] == "treatment"]

        if control.empty or treatment.empty:
            continue

        cr_control = control["conversion_rate"].values[0]
        cr_treatment = treatment["conversion_rate"].values[0]

        lift = (cr_treatment - cr_control) / cr_control

        results.append({
            "platform": platform,
            "country": country,
            "lift": lift
        })

    return pd.DataFrame(results)


def generate_insight(segment_df):
    positive = segment_df[segment_df["lift"] > 0.05]
    negative = segment_df[segment_df["lift"] < -0.02]

    insight = ""

    if not positive.empty:
        top = positive.sort_values(by="lift", ascending=False).iloc[0]
        insight += f"Strongest lift observed in {top['platform']} users in {top['country']}. "

    if not negative.empty:
        worst = negative.sort_values(by="lift").iloc[0]
        insight += f"Negative impact seen in {worst['platform']} users in {worst['country']}. "

    if not positive.empty and not negative.empty:
        insight += "Recommend segmented rollout instead of full release."
    elif not negative.empty:
        insight += "Risk detected. Investigate before rollout."
    else:
        insight += "Consistent positive performance across segments."

    return insight


def main():
    df = load_segment_data()
    segment_df = analyze_segments(df)
    insight = generate_insight(segment_df)

    print("\n--- Segment Insight ---")
    print(insight)


if __name__ == "__main__":
    main()