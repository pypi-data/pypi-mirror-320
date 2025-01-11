from setuptools import setup, find_packages

setup(
    name="ai_feature_store",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "torch",
        "fastapi",
        "uvicorn",
        "scikit-learn",
        "pandas",
        "google-cloud-bigtable",
        "prometheus-client",
    ],
    entry_points={
        "console_scripts": [
            "ai-feature-store=main:main",
        ],
    },
)
