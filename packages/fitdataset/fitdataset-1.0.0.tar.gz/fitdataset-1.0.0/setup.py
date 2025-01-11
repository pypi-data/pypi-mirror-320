from setuptools import setup, find_packages

# Charger la description longue depuis le README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Dépendances requises
required = [
    "certifi>=2024.12.14",
    "charset-normalizer>=3.4.1",
    "idna>=3.10",
    "numpy>=2.2.1",
    "pandas>=2.2.3",
    "python-dateutil>=2.9.0.post0",
    "pytz>=2024.2",
    "requests>=2.32.3",
    "six>=1.17.0",
    "tzdata>=2024.2",
    "xlrd>=2.0.1",
]

# Configuration du package
setup(
    name="fitdataset",
    version="1.0.0",
    packages=find_packages(),
    install_requires=required,
    description="Un package Python pour gérer des datasets nutritionnels dans le cadre du projet FitObjective.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Monsieur Nobody",
    author_email="monsieurnobody01@gmail.com",
    url="https://gitlab.com/misternobody01/fitobjective-dataset.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    include_package_data=True,
    keywords="nutrition dataset pandas fitobjective",
    license="MIT",
)
