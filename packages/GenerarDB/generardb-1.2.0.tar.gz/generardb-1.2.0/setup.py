from setuptools import setup

setup(
    name="GenerarDB",  # Nombre de tu librería
    version="1.2.0",
    description="Librería para manejar bases de datos SQLite con facilidad.",
    url="https://github.com/GhostmanBY/GenerarDB",
    author="Nahuel Romero",
    author_email="nahuelromero2709@gmail.com",
    license="MIT",
    py_modules=["GenerarDB"],  # Archivos de tu módulo
    package_dir={"": "."},  # El directorio base
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
