from setuptools import setup, find_packages

with open("README.md", "r") as f:
    desc = f.read()

setup(
    name="get-papers",
    version="0.3.0",
    description="A tool to fetch and process PubMed papers.",
    author="VIGHNESH M S",
    author_email="vighneshms21@gmail.com",
    packages=find_packages(),
    install_requires=["requests", "pandas"],
    entry_points={
        "console_scripts": [
            "get-papers=scripts.get_papers:main"
        ]
    },
    long_description = desc,
    long_description_type = "text/markdown",

)