from setuptools import setup, find_packages

setup(
    name="pymnz",
    version="0.1.3",
    author="Mateus Menezes",
    author_email="mateusflawer@gmail.com",
    description=(
        "Uma biblioteca para facilitar"
        " a criação de scripts de automações com Python"
    ),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mateusflawer/pymnz",
    packages=find_packages(),
    install_requires=[  # Inclua dependências aqui
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
