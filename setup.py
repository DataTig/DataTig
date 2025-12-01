import setuptools

setuptools.setup(
    name="DataTig",
    version="0.9.0",
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
        "": ["*.html", "*.txt", "*.css", "*.js", "*.png", "*.ttf", "*.woff2"],
    },
    install_requires=[
        "Jinja2<3.1",
        "jsonschema",
        "Pygments",
        "pyyaml",
        "dateparser",
    ],
    extras_require={
        "Dev": [
            "pytest==8.4.2",
            "black==25.9.0",
            "isort==7.0.0",
            "flake8==7.3.0",
            "mypy==1.18.2",
        ],
        "localserver": ["flask"],
    },
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
)
