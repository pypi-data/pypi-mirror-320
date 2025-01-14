from setuptools import setup, find_packages

setup(
    name='jupyno',
    version='1.0.4',
    packages=find_packages(),
    description='Utiliser Arduino dans un notebook Jupyter',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Guillaume Froehlicher',
    author_email='guillaume.froehlicher@ac-rennes.fr',
    license='MIT',
)