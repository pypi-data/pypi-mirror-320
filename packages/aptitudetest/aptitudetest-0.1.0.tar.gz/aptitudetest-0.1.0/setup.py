from setuptools import setup, find_packages

setup(
    name="aptitudetest",
    version="0.1.0",
    description="A Python package for conducting aptitude tests with timed questions.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Abishake",
    author_email="abishake381@gmail.com",
    url="https://github.com/Abishake01/aptitude_quiz",  
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[],
)

