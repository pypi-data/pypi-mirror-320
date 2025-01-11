from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setup(
    name="sqlmodel-fastcrud",
    version="0.1.3",
    description="A reusable CRUD base with filter class for FastAPI applications using SQLModel.",
    author="shareef",
    author_email="your.email@example.com",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "sqlmodel>=0.0.22",
        "fastapi>=0.115.6",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
