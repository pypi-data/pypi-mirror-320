# app/api.py

from fastapi import FastAPI
from app.models import rank_features
from app.storage import store_features
from app.schema import FeatureRequest
from app.data_ingestion import load_data
import pandas as pd

app = FastAPI()

# Load and preprocess data
data = load_data()
X, y = data.iloc[:, :-1], data['target']

@app.get("/get-features/")
def get_features():
    """
    Endpoint to return ranked features.
    """
    ranking = rank_features(X, y)
    return {"features": ranking['Feature'].tolist()}

@app.post("/store-features/")
def store_features_endpoint(request: FeatureRequest):
    """
    Endpoint to store features in Google Bigtable.
    """
    feature_data = pd.DataFrame(request.features.items(), columns=["Feature", "Importance"])
    store_features("iris_features", feature_data)
    return {"status": "success", "message": "Features stored successfully"}
