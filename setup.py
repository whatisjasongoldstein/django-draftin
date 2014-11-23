from distutils.core import setup
from setuptools import find_packages

setup(
    name='Django Draftin',
    version="1.0.0",
    author='Jason Goldstein',
    author_email='jason@betheshoe.com',
    url='https://bitbucket.org/whatisjasongoldstein/django-draftin',
    packages=find_packages(),
    include_package_data=True,
    description='Writing with Draftin.com.',
    long_description=open('README.markdown').read(),
)