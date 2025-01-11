from setuptools import setup, find_packages

setup(
    name="luau-tokenizer",
    version="1.1.1",
    description="Luau Tokenizer for LLM and Luau Code Analysis.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Mars",
    author_email="hexgpcauthor@gmail.com",
    url="https://pypi.org/project/luau-tokenizer/",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
