from setuptools import setup, find_packages
import codecs
import os
import re


here = os.path.abspath(os.path.dirname(__file__))


# Read the version number from a source file.
# Why read it, and not import?
# see https://groups.google.com/d/topic/pypa-dev/0PkjVpcxTzQ/discussion
def find_version(*file_paths):
    # Open in Latin-1 so that we avoid encoding errors.
    # Use codecs.open for Python 2 compatibility
    with codecs.open(os.path.join(here, *file_paths), 'r', 'latin1') as f:
        version_file = f.read()

    # The version line must have the form
    # __version__='ver'
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


install_requires = [
    'numpy==1.16.3',
    'pandas==0.24.2',
    'pyspark==2.4.1',
    'scikit-learn==0.20.3',
    'pyaml==18.11.0',
    'spacy==2.1.3',
    'python-Levenshtein==0.12.0',
    'jsonlines==1.2.0',
    'twine==1.13.0'
]
tests_require = [
    'coverage==4.5.4',
    'pytest==5.1.2'
]
docs_require = [
    'Sphinx==2.0.1',
    'sphinx-rtd-theme==0.4.3',
]
demos_require = [
    'matplotlib==3.0.2',
    # NOTE: demos also require the installation of jupyter
    # but this process is done in scripts/install_jupyter.sh
    # because it requires to configure environment variables
]
extras_require = {
    'tests': install_requires + tests_require,
    'docs': install_requires + docs_require,
    'dev': install_requires + tests_require + docs_require + demos_require,
}

setup(
    name='gmt00-diaman-ai',
    version=find_version('diaman', '__init__.py'),
    include_package_data=True,
    install_requires=install_requires,
    tests_require=tests_require,  # not sure what this is used for as I don't
                                  # see how to install those.
    extras_require=extras_require,

    description="Common utility functions",

    license='DF',
    author="The Data Factory Big data Team.",
    author_email="datafactory@mpsa.com",
    url="",
    download_url='',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering',
    ],

    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'train-diaman=diaman.pipeline.cli:cli'
        ]
    }
)
