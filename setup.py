__author__="HP Envy"
__date__ ="$Jan 11, 2015 1:57:59 PM$"

from setuptools import setup,find_packages

setup (
  name = 'RootIO Web',
  version = '0.1',
  packages = find_packages(),

  # Declare your packages' dependencies here, for eg:
  install_requires=['foo>=3'],

  # Fill in these to make your Egg ready for upload to
  # PyPI
  author = 'HP Envy',
  author_email = '',

  summary = 'Just another Python package for the cheese shop',
  url = '',
  license = '',
  long_description= 'Long description of the package',

  # could also include long_description, download_url, classifiers, etc.

  
)