from setuptools import setup, find_packages

setup(
    name="npscoder",  # Nom de votre package
    version="0.1.0",  # Version initiale
    packages=find_packages(where="src"),  # Trouve tous les sous-packages dans `src`
    package_dir={"": "src"},  # Indique que les packages sont dans `src`
    description="Non Parametric Supervised Coder",  # Description courte
    long_description=open("README.md").read(),  # Description longue (depuis le README)
    long_description_content_type="text/markdown",
    author="Benoit Rognier",  # Votre nom
    license="MIT",  # Licence du projet
    install_requires=[
        "pandas",  # Ajoutez les dépendances nécessaires ici
        "numpy",
        "typing",
        "typing-extensions",
        "IPython",
        "matplotlib",
        "scipy",
        "statsmodels",
        "python-dateutil",
        "pandas",
        "numpy",
        "dataclasses"
    ],
    python_requires=">=3.13",  # Version minimale de Python
)