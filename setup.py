from setuptools import setup, find_packages
import os

long_description = 'cf_clus is a ClowdFlows package for inducing Predictive Clustering Trees with CLUS.'

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
]

dist = setup(
    name='cf_clus',
    version='1.0.5',
    author='Janez Kranjc',
    description='Induce predictive clustering trees in ClowdFlows.',
    long_description=long_description,
    author_email='janez.kranjc@gmail.com',
    url='https://github.com/xflows/cf_clus',
    license = 'GPL',
    install_requires=['liac-arff',],
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
