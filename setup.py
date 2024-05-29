import setuptools

setuptools.setup(
    name="DataTig",
    version="0.5.0",
    description="DataTig helps you crowdsource and use data stored in files in a git repository.",
    long_description="DataTig helps you crowdsource and use data stored in files in a git repository.",
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
