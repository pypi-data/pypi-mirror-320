from setuptools import setup, find_packages

setup(
    name='wiseprophet',
    version='0.0.9',
    description='WiseProphet Platform package creation written by wiseitech',
    author='wiseitech',
    author_email='jskwon@wise.co.kr',
    url='https://wise.co.kr',
    install_requires=['joblib', 'pandas', 'scikit-learn','h5py','dask','hdfs','requests'],
    packages=find_packages(exclude=[]),
    keywords=['automl', 'ai', 'wiseitech', 'mlops'],
    python_requires='>=3.7',
    package_data={},
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)