from setuptools import setup, find_packages

setup(
    name="sqlmodel-fastcrud",
    version="0.1.1",
    description="A reusable CRUD base with filter class for FastAPI applications using SQLModel.",
    author="shareef",
    author_email="your.email@example.com",
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
