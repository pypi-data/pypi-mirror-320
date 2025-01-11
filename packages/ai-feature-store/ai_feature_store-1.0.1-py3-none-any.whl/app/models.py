# app/models.py

import torch
import torch.nn as nn
from sklearn.ensemble import GradientBoostingClassifier
import pandas as pd

class Autoencoder(nn.Module):
    def __init__(self, input_dim):
        super(Autoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.Linear(64, input_dim),
            nn.Sigmoid()
        )

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return encoded, decoded

def train_autoencoder(data):
    model = Autoencoder(input_dim=data.shape[1])
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    for epoch in range(50):
        inputs = torch.tensor(data.values, dtype=torch.float32)
        encoded, decoded = model(inputs)
        loss = criterion(decoded, inputs)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    print("Training Complete")
    return model

def rank_features(X, y):
    """
    Rank features using a Gradient Boosted Classifier.

    Args:
        X (pd.DataFrame): Feature matrix.
        y (pd.Series): Target variable.

    Returns:
        pd.DataFrame: DataFrame with features and their importance scores.
    """
    gbc = GradientBoostingClassifier()
    gbc.fit(X, y)
    feature_importances = gbc.feature_importances_
    return pd.DataFrame({'Feature': X.columns, 'Importance': feature_importances}).sort_values(by='Importance', ascending=False)
