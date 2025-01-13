from setuptools import setup, find_packages

setup(
    name='InnoML',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'numpy',
    ],
    author='Sriram',
    author_email='sriramachandranram@gmail.com',
    description='A collection of machine learning models implemented from scratch',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/SriramR123/InnoML',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)