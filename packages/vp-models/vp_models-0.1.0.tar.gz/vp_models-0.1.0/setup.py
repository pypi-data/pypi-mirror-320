from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vp_models",  # Ensure the name is unique on PyPI
    version="0.1.0",  # Follow semantic versioning
    author="Vishnupriya K",
    author_email="vishnupriyakarthy@gmail.com",
    description="A package for machine learning models and utilities",
    long_description=long_description,  # Include README content
    long_description_content_type="text/markdown",
    url="https://github.com/vishnupriya230604/vp_models.git",  # GitHub repo URL
    packages=find_packages(),  # Automatically discover all packages and subpackages
    install_requires=[
        "numpy>=1.21.0",  # Specify minimum versions if needed
        "scikit-learn>=1.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "vp_models=main:main",  # Replace `main` with your actual script/module name
        ]
    },

)
