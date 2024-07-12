import setuptools

setuptools.setup(
    name="DataTig",
    version="0.6.0",
    description="DataTig helps you crowdsource and use data stored in files in a git repository.",
    long_description_content_type="text/markdown",
    long_description="DataTig helps you crowdsource and use data stored in files in a git repository.\n\n"
    + "Home Page: [https://www.datatig.com](https://www.datatig.com)\n\n"
    + "Documentation: [https://datatig.readthedocs.io/en/latest/](https://datatig.readthedocs.io/en/latest/)\n\n"
    + "Issues: [https://github.com/DataTig/DataTig/issues](https://github.com/DataTig/DataTig/issues)\n\n"
    + "Source: [https://github.com/DataTig/DataTig](https://github.com/DataTig/DataTig)",
    url="https://github.com/DataTig/DataTig",
    project_urls={
        "Home Page": "https://www.datatig.com",
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
    install_requires=[
        "Jinja2<3.1",
        "jsonschema",
        "Pygments",
        "pyyaml",
        "dateparser",
        "pytz",
    ],
    extras_require={
        "Dev": [
            "pytest==7.1.2",
            "black==22.6.0",
            "isort==5.10.1",
            "flake8==4.0.1",
            "mypy==0.971",
        ],
        "localserver": ["flask"],
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
