import setuptools


setuptools.setup(
    name="DataTig", 
    version="0.0.1",
    packages=setuptools.find_packages(exclude=['test']),
    package_data={
        "": ["*.html", "*.txt", "*.css"],
    },
    classifiers=[
    ],
    install_requires=['Jinja2','spreadsheetforms'] ,
    python_requires='>=3.6',
)
