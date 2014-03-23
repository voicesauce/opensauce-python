__author__ = 'kate'

from distutils.core import setup

files = ["opensauce/*"]

setup(name = "opensauce-python",
      version="0.0.0",
      description="stuff",
      author="kate",
      author_email="ksilvers@umass.edu",
      url="here",
      packages=['opensauce'],
      package_data = {'opensauce': files},
      scripts = ["runner", "test"],
      long_description = """ stuff """
      )