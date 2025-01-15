from setuptools import setup, find_packages

setup(
    name="minipiler",  
    version="0.0.1",  
    author="Artur Arantes Santos da Silva",
    author_email="minipiler@arturarantes.com",
    description="This is a package reserved for a future project.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    # url="https://github.com/seu_usuario/minipiler",  
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
