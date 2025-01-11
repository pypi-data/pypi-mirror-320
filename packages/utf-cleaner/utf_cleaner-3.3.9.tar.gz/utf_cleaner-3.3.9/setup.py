from setuptools import setup, find_packages

setup(
    name="utf-cleaner",
    version="3.3.9",
    description="A powerful package that removes non-UTF characters from strings.",
    author="John Doe",
    author_email="john@doe.com",
    url="https://github.com/john-doe/utf_cleaner",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)