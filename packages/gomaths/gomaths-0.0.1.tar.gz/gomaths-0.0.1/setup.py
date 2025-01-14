from setuptools import setup, find_packages

setup(
    name='gomaths',
    version='0.0.1',
    packages=find_packages(),
    description='A simple package of mathematics(beta test)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Soso',
    author_email='soribasoriba94@gmail.com',
    url='https://github.com/soso080/gomaths',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[],
)