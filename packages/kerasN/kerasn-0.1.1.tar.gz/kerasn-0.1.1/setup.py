from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kerasN",
    version="0.1.1",
    author="Yeseol Lee",
    author_email="yebubu00@gmail.com",
    description="A pure Python/NumPy implementation of deep learning framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AshleyLee00/KerasN",
    project_urls={
        "Bug Tracker": "https://github.com/AshleyLee00/KerasN/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.2",
        "matplotlib>=3.3.2",
        "scikit-learn>=0.23.2",
        "pandas>=1.2.0",
    ],
) 