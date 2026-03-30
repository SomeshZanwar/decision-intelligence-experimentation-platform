import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import os
from dotenv import load_dotenv
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from python.stats.experiment_analysis import compute_stats, decision_logic
from python.stats.insight_generator import analyze_segments, generate_insight

load_dotenv()

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

st.title("Experiment Decision Intelligence Dashboard")

# Load data
metrics = pd.read_sql("SELECT * FROM fct_experiment_metrics", engine)
segments = pd.read_sql("SELECT * FROM fct_experiment_segments", engine)

# Compute stats
stats = compute_stats(metrics)
decision = decision_logic(stats)

# Insight
seg_analysis = analyze_segments(segments)
insight = generate_insight(seg_analysis)

# Display
st.subheader("Experiment Results")

st.write(f"Control CR: {stats['control_cr']:.4f}")
st.write(f"Treatment CR: {stats['treatment_cr']:.4f}")
st.write(f"Lift: {stats['lift']*100:.2f}%")
st.write(f"P-value: {stats['p_value']:.5f}")

st.success(f"Decision: {decision}")

st.subheader("Segment Insight")
st.info(insight)

st.subheader("Raw Metrics")
st.dataframe(metrics)

st.subheader("Segment Breakdown")
st.dataframe(segments)