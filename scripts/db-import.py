import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
database_db = os.getenv("CLINOPS_DB")
database_user = os.getenv("CLINOPS_USER")
database_password = os.getenv("CLINOPS_PASSWORD")

print("DEBUG: database_db = {}".format(database_db))
print("DEBUG: database_user = {}".format(database_user))
print("DEBUG: database_password = {}".format(database_password))

conn_string = f"postgresql://{database_user}:{database_password}@postgres/{database_db}"

db = create_engine(conn_string)

# the folder containing the CSV files
path = "."

# the list of CSV file names
files = [f for f in os.listdir(path) if f.endswith(".csv")]

# Remove spaces and lowercase file names, then load them into the database
try:
    with db.connect() as conn:
        for file in files:
            df = pd.read_csv(os.path.join(path, file))
            # Lowercase column names, replace spaces and hyphens with underscores
            df.columns = [
                col.lower().replace(" ", "_").replace("-", "_") for col in df.columns
            ]
            # Generate table name by removing spaces, hyphens and converting to lowercase
            table_name = (
                "raw_"
                + file.replace(" ", "_").replace("-", "_").replace(".csv", "").lower()
            )
            # Load DataFrame into PostgreSQL
            df.to_sql(table_name, con=conn, if_exists="replace", index=False)
except Exception as e:
    # Redact password in connection string for error message
    redacted_conn_string = f"postgresql://{database_user}:***@postgres/{database_db}"
    print(f"ERROR: Failed to connect to the database using connection string: {redacted_conn_string}")
    print(f"Exception: {e}")
    exit(1)
