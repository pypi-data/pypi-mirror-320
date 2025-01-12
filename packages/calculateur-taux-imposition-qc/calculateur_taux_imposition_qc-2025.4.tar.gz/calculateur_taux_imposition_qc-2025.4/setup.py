from setuptools import setup, find_packages

setup(
    name="calculateur_taux_imposition_qc",
    description="Calculateur de taux d'imposition pour particuliers pour le Québec",
    author="Samuel Paquette-Paré",
    author_email="paquetteparesamuel@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
