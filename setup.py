from setuptools import setup

def readme():
    with open('README.rst', 'r') as f:
        return f.read()

setup(
    name = 'pygame_ai',
    version = '0.1',
    description = 'AI module for 2D pygame games',
    long_description = 'Nothing else',
    classifiers = [
        'Programming Language :: Python :: 3.6',
        'Topic :: Libraries :: pygame'
    ],
    keywords = 'pygame ai steering',
    url = 'notyet',
    author = 'Nek',
    author_email = 'nek2712@gmail.com',
    license = 'none yet',
    packages = ['pygame_ai'],
    install_requires = [
        'pygame'
    ],
    include_package_data = True,
    zip_safe = False
)
