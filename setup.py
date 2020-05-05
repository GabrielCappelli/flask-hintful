import pathlib

from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="flask-hintful",
    version="0.0.5",
    description="Flask extension for generating restful apis using type hints to automatically (de)serialize parameters and generate openapi docs.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/GabrielCappelli/flask-hintful",
    author="Gabriel Cappelli",
    author_email="6148081+GabrielCappelli@users.noreply.github.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["flask_hintful"],
    include_package_data=True,
    install_requires=[
        'flask>=1.0.2',
        'openapi-specgen',
        'marshmallow<3'
    ],
    entry_points={}
)
