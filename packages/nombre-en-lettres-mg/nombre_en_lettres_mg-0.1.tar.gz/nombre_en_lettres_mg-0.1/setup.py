from setuptools import setup, find_packages

setup(
    name="nombre_en_lettres_mg",  # Nom de la bibliothèque
    version="0.1",  # Version initiale
    packages=find_packages(),  # Trouve tous les packages dans le dossier
    description="Une bibliothèque pour convertir les nombres en lettres en malagasy.",
    long_description=open("README.md").read(),  # Description longue dans le README.md
    long_description_content_type="text/markdown",
    author="Day Lamy",  # Votre nom
    author_email="hatsudai1@gmail.com",  # Votre email
    url="https://github.com/Daylamiy06",  # Lien vers votre GitHub
    license="Propriétaire",  # Type de licence (propriétaire)
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",  # Licence propriétaire
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Version minimale de Python
)
