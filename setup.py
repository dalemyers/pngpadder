#!/usr/bin/env python

from os import path

from setuptools import setup, find_packages


def run_setup():
    """Run package setup."""
    here = path.abspath(path.dirname(__file__))

    # Get the long description from the README file
    try:
        with open(path.join(here, 'README.md')) as f:
            long_description = f.read()
    except:
        # This happens when running tests
        long_description = None

    setup(
        name='pngpadder',
        version='0.3',
        description='A tool for padding PNG files to specific sizes',
        long_description=long_description,
        url='https://github.com/dalemyers/pngpadder',
        author='Dale Myers',
        author_email='dale@myers.io',
        license='MIT',
        scripts=['command_line/pngpadder'],

        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Topic :: Utilities'
        ],

        keywords='png',
        packages=find_packages(exclude=['docs', 'tests'])
    )

if __name__ == "__main__":
    run_setup()
