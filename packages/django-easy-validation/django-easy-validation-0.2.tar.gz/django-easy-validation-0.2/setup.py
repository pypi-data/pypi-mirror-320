# setup.py
from setuptools import setup
from os.path import join

long_description = (
    open('README.md').read())

setup(
    name='django-easy-validation',
    version='0.2',
    description='Easy Validation for Django based projects especially for Ajax based request.',
    long_description_content_type='text/markdown',
    long_description=long_description,
    url='https://github.com/sandysh/django-easy-validation',
    author='Sandesh Satyal',
    author_email='sandeshsatyal@gmail.com',
    license='MIT',
    zip_safe=False,
    keywords='django-easy-validation validation form-validation form ajax ajax-validation easy-validation',
)
