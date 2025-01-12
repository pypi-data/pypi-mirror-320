from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='wrh',
    version='0.8',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    description='Package for CIV550 course and UofT.',
    url='https://wrh.civmin.utoronto.ca/',
    author='Mohammed Basheer',
    author_email='mohammedadamabbaker@gmail.com',
    install_requires=['click','pandas','numpy','scipy','platypus-opt','tables', 'pywr'],
    packages=find_packages(),
    package_data={
        'wrh': ['json/*.json'],
    },
    entry_points={
        'console_scripts': ['wrh=wrh.cli:start_cli'],
    },
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'Natural Language :: English'
    ]
)
