from setuptools import setup, find_packages

setup(
    name='quickbytes',
    version='0.1.0',
    description='A lightweight data manipulation library like pandas',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your-email@example.com',
    url='https://github.com/yourusername/bytes',
    packages=find_packages(),
    install_requires=[],
    python_requires='>=3.6',
)
