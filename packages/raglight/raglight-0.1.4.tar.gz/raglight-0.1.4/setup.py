from setuptools import setup, find_packages

setup(
    name="raglight",  # Nom du package sur PyPI
    version="0.1.4",  # Numéro de version
    description="A lightweight and modular framework for Retrieval-Augmented Generation (RAG)",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Labess40",
    author_email="",
    url="https://github.com/Bessouat40/RAGLight",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "langchain",
        "chromadb",
        "python-dotenv",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)
