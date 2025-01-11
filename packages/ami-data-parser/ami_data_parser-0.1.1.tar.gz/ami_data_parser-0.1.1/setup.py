from setuptools import setup


with open("README.md", "r") as arq:
    readme = arq.read()

setup(
    name='ami-data-parser',
    version='0.1.1',
    license='MIT License',
    author='Tatianno Alves',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='tferreiraalves@gmail.com',
    keywords='asterisk manager interface ami parser data',
    description=u'AMI parser data',
)