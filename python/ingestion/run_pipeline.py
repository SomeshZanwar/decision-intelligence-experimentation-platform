
import subprocess
import sys

python_exec = sys.executable  # this ensures venv python is used

print("Resetting tables...")
subprocess.run([
    "psql",
    "-U", "postgres",
    "-h", "127.0.0.1",
    "-d", "experiment_db",
    "-f", "sql/reset_tables.sql"
], check=True)

print("Generating and loading data...")
subprocess.run(
    [python_exec, "python/data_generation/generate_experiment_data.py"],
    check=True
)

print("Validating data...")
subprocess.run(
    [python_exec, "python/ingestion/validate_data.py"],
    check=True
)

print("Pipeline completed successfully.")