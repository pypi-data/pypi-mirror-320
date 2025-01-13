from setuptools import setup, find_packages
from pathlib import Path

setup(
    name="PureAI",
    version="0.0.1",
    description="all-in-one solution for building Retrieval-Augmented Generation(RAG) pipelines with ease and efficiency",
    author="PureAI",
    author_email="guilherme.romanini@pureai.com.br",
    include_package_data=True,
    packages=find_packages(),
    package_data={
        "pureai": ["RagPUREAI.so"]
    },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
