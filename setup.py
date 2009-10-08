from setuptools import setup, find_packages
import os

version = '2.1dev'

setup(name='silva.core.services',
      version=version,
      description="Silva Services",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='silva core services',
      author='Infrae',
      author_email='info@infrae.com',
      url='https://infrae.com/products/silva',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['silva', 'silva.core'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'five.grok',
          'silva.core.interfaces',
          ],
      )
