from setuptools import setup, find_packages

setup(
    name="nisi",  # Package name on PyPI
    version="0.1.0",  # Version of your package
    description="Solutions for NNDL questions",
    author="Your Name",
    author_email="your_email@example.com",
    url="https://github.com/yourusername/nisi",  # GitHub repo (optional)
    packages=find_packages(),  # Automatically find packages in the project
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)