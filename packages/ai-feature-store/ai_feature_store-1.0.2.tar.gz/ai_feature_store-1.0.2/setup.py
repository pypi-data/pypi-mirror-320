from setuptools import setup, find_packages

# Read the contents of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai_feature_store",
    version="1.0.2",
    author="Ashish Verma",
    author_email="averm004@odu.edu",
    description="A package for feature engineering and scalable storage with Google Bigtable.",
    long_description=long_description,
    long_description_content_type="text/markdown",  # Important for rendering Markdown on PyPI
    url="https://github.com/ashishodu2023/ai_feature_store",  # Update with your repo URL
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
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "ai-feature-store=main:main",
        ],
    },
)
