from distutils.core import setup
from setuptools import find_packages

setup(
    name='Django Draftin',
    version="1.1.0",
    author='Jason Goldstein',
    author_email='jason@betheshoe.com',
    url='https://www.github.com/whatisjasongoldstein/django-draftin',
    packages=find_packages(),
    include_package_data=True,
    description='Why write in a CMS?',
    long_description=open('README.markdown').read(),
)