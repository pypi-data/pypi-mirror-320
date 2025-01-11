from setuptools import setup, find_packages

setup(
    name="text_embeddings_10d",
    version="0.1.0",
    description="Text embeddings package with multiple model support",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
        "sentence-transformers>=2.2.0",
        "openai>=1.0.0",
        "beautifulsoup4>=4.9.3",
        "requests>=2.25.1",
        "tqdm>=4.64.0"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)