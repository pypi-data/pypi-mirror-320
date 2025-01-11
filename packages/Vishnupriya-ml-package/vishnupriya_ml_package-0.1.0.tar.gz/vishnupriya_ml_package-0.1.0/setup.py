from setuptools import setup, find_packages

setup(
    name="Vishnupriya_ml_package",  # Name of your package
    version="0.1.0",  # Initial version
    author="Vishnupriya K",
    author_email="vishnupriyakarthy@gmail.com",
    description="A package for machine learning models and utilities",
    # long_description=open("README.md").read(),
    # long_description_content_type="text/markdown",
    url="https://github.com/vishnupriya230604/my_ML_package",  # Replace with your GitHub repo URL
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scikit-learn",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "my_ml_package=main:main",
        ]
    },
)
