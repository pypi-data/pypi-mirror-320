from setuptools import setup, find_packages

setup(
    name="ayeirus_models",
    version="0.1.0",
    author="Surieya",
    description="A package implementing common ML algorithms",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "scikit-learn",
    ],
    python_requires=">=3.6",
)
