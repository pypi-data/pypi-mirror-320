from setuptools import setup, find_packages

setup(
    name="xml-formatter-plus",
    version="0.1.1",
    author="Yash Kabra",
    author_email="yash11kabra@gmail.com",
    description="A Python package that formats and beautifies XML strings with HTML entity handling",
    url="https://github.com/yash11K/html-escape",
    packages=find_packages(),
    py_modules=["xml_formatter"],
    entry_points={
        "console_scripts": [
            "xml-formatter=xml_formatter:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
