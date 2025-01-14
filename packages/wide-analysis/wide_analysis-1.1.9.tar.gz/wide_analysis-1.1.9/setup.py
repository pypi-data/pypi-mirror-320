from setuptools import setup, find_packages

setup(
    name='wide_analysis',
    version='1.1.9',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pandas',
        'transformers',
        'datasets',
        'torch',
        'openai',
        'tiktoken',
        'beautifulsoup4',
        'requests',
        'pysbd',

    ],
    entry_points={
        'console_scripts': [
            # Define command-line scripts here if needed

        ],
    },
    author='Hsuvas Borkakoty',
    author_email='hsuvas@gmail.com',
    description='A package for analyzing Wikipedia deletion discussions.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/hsuvas/wide_analysis',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    package_data={
        'wide_analysis': ['asset/Wide_Analysis_overall.png']
    },
)
