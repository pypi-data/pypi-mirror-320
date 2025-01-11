from setuptools import setup, find_packages

setup(
    name='shasha',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'numpy',
    ],
    author='Shabari Prakash',
    author_email='shabariprakashsv@gmail.com',
    description='A collection of machine learning models implemented from scratch',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/shabari48/shasha',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
