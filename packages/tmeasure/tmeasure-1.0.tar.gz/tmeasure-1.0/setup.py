from setuptools import setup, find_namespace_packages

setup(
    name="tmeasure",
    url="https://github.com/tboulet/PythonTimeMeasure", 
    author="Timothé Boulet",
    author_email="timothe.boulet0@gmail.com",
    
    packages=find_namespace_packages(),

    version="1.0",
    license="MIT",
    description="Time measure tool for python",
)