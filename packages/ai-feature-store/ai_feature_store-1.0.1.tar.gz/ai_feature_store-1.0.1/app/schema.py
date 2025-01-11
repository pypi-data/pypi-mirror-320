# app/schema.py

from pydantic import BaseModel

class FeatureRequest(BaseModel):
    features: dict  # Expected format: {"Feature Name": Importance Score}
