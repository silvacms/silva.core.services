# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt
from setuptools import setup, find_packages
import os

version = '3.0dev'

tests_require = [
    'Products.Silva [test]',
    ]

setup(name='silva.core.services',
      version=version,
      description="Silva Services",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='silva core services',
      author='Infrae',
      author_email='info@infrae.com',
      url='https://infrae.com/products/silva',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src', exclude=['ez_setup']),
      namespace_packages=['silva', 'silva.core'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Products.ZCatalog',
        'five.grok',
        'five.intid',
        'setuptools',
        'silva.core.conf',
        'silva.core.interfaces',
        'zope.component',
        'zope.interface',
        'zope.intid',
        'zope.schema',
        ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
