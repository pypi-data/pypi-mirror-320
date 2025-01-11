from setuptools import setup, find_packages

setup(
    name="algo-bhanu",
    version="1.1.0",
    author="bhanu_2025abc",
    author_email="citbhanupriya@gmail.com",
    description="A short description of the package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/bhanupriya03m/algo",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12"
)

