import setuptools

setuptools.setup(
    name="DataTig",
    version="0.2.0",
    description="A tool for working with crowd sourced data in JSON files in a Git repository",
    long_description="A tool for working with crowd sourced data in JSON files in a Git repository",
    url="https://github.com/DataTig/DataTig",
    project_urls={
        "Documentation": "https://datatig.readthedocs.io/en/latest/",
        "Issues": "https://github.com/DataTig/DataTig/issues",
        "Source": "https://github.com/DataTig/DataTig",
    },
    author="Open Data Services",
    author_email="code@opendataservices.coop",
    license="MIT",
    packages=setuptools.find_packages(exclude=["test"]),
    package_data={
        "": ["*.html", "*.txt", "*.css", "*.js"],
    },
    classifiers=[],
    install_requires=["Jinja2", "spreadsheetforms", "jsonschema", "Pygments", "pyyaml"],
    extras_require={"Dev": ["pytest", "black", "isort", "flake8"]},
    python_requires=">=3.6",
)
