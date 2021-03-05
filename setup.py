import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pypatconsole", 
    version="0.0.9",
    author="Naphat Amundsen",
    author_email="naphat@live.com",
    description="Simple and sexy console interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Napam/PyPat-Console",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)