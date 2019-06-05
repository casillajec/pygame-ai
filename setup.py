from setuptools import setup

def readme():
    with open('README.rst', 'r') as f:
        return f.read()

setup(
    name = 'pygame_ai',
    version = '0.1',
    description = 'Videogame AI package for PyGame',
    long_description = 'Implements a set of common AI techniques used in videogame development',
    classifiers = [
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: pygame'
    ],
    keywords = 'pygame ai steering',
    url = 'https://github.com/nek2712/pygame-ai',
    author = 'Nek',
    author_email = 'nek2712@gmail.com',
    license = 'GLGPL v2.1',
    packages = ['pygame_ai'],
    install_requires = [
        'pygame'
    ],
    include_package_data = True,
    zip_safe = False
)
