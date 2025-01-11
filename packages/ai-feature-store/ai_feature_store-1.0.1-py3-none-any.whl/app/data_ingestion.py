# app/data_ingestion.py

from sklearn.datasets import load_iris
import pandas as pd

def load_data():
    """
    Load the Iris dataset as a pandas DataFrame.

    Returns:
        pd.DataFrame: Dataset with features and target column.
    """
    iris = load_iris()
    data = pd.DataFrame(iris.data, columns=iris.feature_names)
    data['target'] = iris.target
    return data
