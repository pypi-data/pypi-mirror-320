from setuptools import setup, find_packages

setup(
    name="dtlibpc",
    version="1.0.4",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    description="A package to validate domain and manage dataset access.",
    author="GTrip",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
