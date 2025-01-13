from os import path
from setuptools import find_namespace_packages, setup

from huscy.participations import __version__


with open(path.join(path.abspath(path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='huscy.participations',
    version=__version__,
    license='AGPLv3+',

    description='huscy.participations',
    long_description=long_description,
    long_description_content_type='text/markdown',

    author='Stefan Bunde',
    author_email='stefanbunde+git@posteo.de',

    url='https://bitbucket.org/huscy/participations',

    packages=find_namespace_packages(include=['huscy.*']),

    install_requires=[
        'huscy.attributes',
        'huscy.bookings',
        'huscy.project_design',
    ],
    extras_require={
        'development': ['psycopg2-binary'],
        'testing': ['tox', 'watchdog'],
    },

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
    ],
)
