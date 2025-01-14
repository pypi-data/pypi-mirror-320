from setuptools import setup, find_packages

setup(
    name='moneyline',
    version='0.2.0',
    author='spogtrop',
    author_email='spogtrop@gmail.com',
    description='Python package meant to ease the use of the LiveOdds API to find arbitrage opportunities',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    #url='https://github.com/yourusername/doovpy',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)