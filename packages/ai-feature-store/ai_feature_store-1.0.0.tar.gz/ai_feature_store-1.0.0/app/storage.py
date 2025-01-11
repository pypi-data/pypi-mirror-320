import os
from google.cloud import bigtable
from google.cloud.bigtable import column_family
import pandas as pd

# Programmatically set GOOGLE_APPLICATION_CREDENTIALS
SERVICE_ACCOUNT_KEY_PATH = "keys.json"
if not os.path.exists(SERVICE_ACCOUNT_KEY_PATH):
    raise FileNotFoundError(f"Service account key not found at: {SERVICE_ACCOUNT_KEY_PATH}")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_KEY_PATH

def create_table_if_not_exists(instance, table_name, column_family_name):
    """
    Create a Bigtable table with the specified column family if it does not exist.

    Args:
        instance (bigtable.instance.Instance): Bigtable instance.
        table_name (str): Name of the table to create.
        column_family_name (str): Name of the column family to create.
    """
    table = instance.table(table_name)

    # Check if the table exists
    if not table.exists():
        print(f"Table '{table_name}' does not exist. Creating table...")
        table.create()
        cf = table.column_family(column_family_name)
        cf.create()
        print(f"Table '{table_name}' with column family '{column_family_name}' created successfully.")
    else:
        print(f"Table '{table_name}' already exists.")

def store_features(table_name, feature_data):
    """
    Store feature rankings in Google Bigtable.

    Args:
        table_name (str): Name of the Bigtable table.
        feature_data (pd.DataFrame): DataFrame with features and importance scores.
    """
    try:
        # Initialize Bigtable client
        client = bigtable.Client(admin=True)
        instance = client.instance("feature-store-instance")

        # Ensure the table and column family exist
        create_table_if_not_exists(instance, table_name, "metadata")

        table = instance.table(table_name)

        print("Storing the following data in Bigtable:")
        print(feature_data)

        # Store features in Bigtable
        for idx, row in feature_data.iterrows():
            row_key = f"feature-{idx}"  # Each feature gets a unique row key
            direct_row = table.direct_row(row_key)
            direct_row.set_cell("metadata", "name", row["Feature"])
            direct_row.set_cell("metadata", "importance", str(row["Importance"]))
            direct_row.commit()

        print("Features stored successfully in Bigtable!")
    except Exception as e:
        print(f"Error storing features in Bigtable: {e}")
