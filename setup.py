from setuptools import setup, find_packages

setup(
    name="dsa-dashboard",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "streamlit==1.28.0",
        "pandas==2.1.4",
        "numpy==1.24.3",
        "plotly==5.17.0",
        "openpyxl==3.1.2",
    ],
    python_requires=">=3.8",
)
