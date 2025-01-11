from setuptools import setup, find_packages

setup(
    name='ZScoreCalculator',
    version='1.0.0',
    author='Lillian Tatka',
    description="""A package for calculating peptide and protein z scores.""",
    packages=find_packages(), 
    install_requires=[ 
        'pandas',
        'numpy',
        'tqdm',
        'matplotlib',
        'seaborn',
	'scipy',
	'statsmodels',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',

)
