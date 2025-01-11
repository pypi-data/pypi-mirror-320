from sklearn.ensemble import GradientBoostingClassifier

def rank_features(X, y):
    gbc = GradientBoostingClassifier()
    gbc.fit(X, y)
    feature_importances = gbc.feature_importances_
    return pd.DataFrame({'Feature': X.columns, 'Importance': feature_importances}).sort_values(by='Importance', ascending=False)
