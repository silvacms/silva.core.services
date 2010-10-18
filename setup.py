from setuptools import setup, find_packages
import os

version = '2.3.1dev'

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
          'setuptools',
          'five.grok',
          'five.intid',
          'silva.core.conf',
          'silva.core.interfaces',
          'zope.component',
          'zope.interface',
          'zope.intid',
          'zope.lifecycleevent'
          ],
      )
