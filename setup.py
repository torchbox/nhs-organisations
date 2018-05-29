import os
from setuptools import setup, find_packages
from nhsorganisations import __version__, stable_branch_name

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

base_url = "https://bitbucket.org/rkhleics/nhs-organisations"
dowload_url = '%starball/v%s' % (base_url, __version__)
branch_url = "%stree/stable/%s" % (base_url, stable_branch_name)

# Testing dependencies
testing_extras = [
    'coverage',
]

setup(
    name="nhs-organisations",
    version=__version__,
    author="Andy Babic",
    author_email="ababic@rkh.co.uk",
    description=("A tiny app to help you store, use and update NHS Organisation data in your Django project"),
    long_description=README,
    packages=find_packages(),
    license="MIT",
    keywords="django nhs data model utility",
    download_url=dowload_url,
    url=branch_url,
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Topic :: Internet :: WWW/HTTP',
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires='>=3.5,<3.8',
    install_requires=[
        "requests",
    ],
    extras_require={
        'testing': testing_extras,
    },
)
