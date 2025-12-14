# Energy Price Forecasting System - Package Setup
from setuptools import setup, find_packages

setup(
    name="energy-price-forecasting",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.31.0",
        "pandas>=2.2.0",
        "numpy>=1.26.0",
        "python-dotenv>=1.0.0",
        "tenacity>=8.2.3",
    ],
    extras_require={
        "test": [
            "pytest>=7.4.3",
            "pytest-mock>=3.12.0",
            "pytest-cov>=4.1.0",
        ],
    },
)

