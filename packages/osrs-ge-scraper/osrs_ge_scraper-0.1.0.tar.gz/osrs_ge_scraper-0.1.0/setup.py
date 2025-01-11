from setuptools import setup, find_packages

setup(
    name='osrs_ge_scraper',
    version='0.1.0',
    description='A Python package to scrape the Old School RuneScape Grand Exchange API',
    author='Christian Hatton',
    author_email='c63513389@gmail.com',
    url='https://github.com/syntaxskater/osrs_ge_scraper',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
