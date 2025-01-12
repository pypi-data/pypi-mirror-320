from setuptools import setup, find_packages

setup(
    name="cbe-verification-sdk",
    version="1.4.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "PyPDF2>=3.0.0"
    ],
    author="Naod Yeshiwas",
    author_email="yegnadevelopers@gmail.com",
    description="SDK for CBE Transaction Verification API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/NaodYeshiwas/CBE-Verification-API",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
) 