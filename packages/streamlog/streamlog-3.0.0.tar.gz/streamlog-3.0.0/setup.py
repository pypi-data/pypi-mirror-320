from setuptools import setup, find_packages

# Read the long description from the README.md file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="streamlog",
    version="3.0.0",
    author="Prathmesh Soni",
    author_email="info@soniprathmesh.com",
    description="A Python package to send print statements to an API while printing to the console.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PrathmeShsoni/StreamLog",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "pytz",
        "requests",
        "lxml"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    keywords="streamlog stream log api print",
)
