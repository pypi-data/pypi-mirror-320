from setuptools import setup, find_packages

import os

here = os.path.abspath(os.path.dirname(__file__))


VERSION = '0.1'
DESCRIPTION = 'Just Testing'

# Setting up
setup(
    name="calculator__ONLY__FOR__TESTING",
    version=VERSION,
    author="nezar",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'calculator'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)