from setuptools import setup, find_packages

setup(
    name="dtlibpc",
    version="1.0.6",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    description="A package to manage datasets.",
    author="GTrip",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    package_data={
        "dtlibpc": ["dataset.so", 'utils.so'],  # Include dataset.so in the package
    },
    include_package_data=True,  # Ensure package_data is processed
)
