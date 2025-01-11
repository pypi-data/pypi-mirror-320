from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dobletau-quant",  # Nombre del paquete en PyPI
    version="1.0.6",
    author="Percy Guerra Peña",
    author_email="percy.guerra1@unmsm.edu.pe",
    description="API para participar en una competencia de trading algoritmico.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/dobletau-quant/",  # Reemplaza con la URL de tu repositorio
    packages=find_packages(),
    install_requires=[
        "requests>=2.20.0",
        "pandas>=1.0.0",
    ],
    license="MIT",  # Campo explícito para la licencia
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
