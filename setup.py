from setuptools import setup, find_packages
import os

version = '4.0b2'

setup(name='genweb.core',
      version=version,
      description="Genweb core package",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='genweb',
      author='UPCnet Plone Team',
      author_email='plone.team@upcnet.es',
      url='https://dev.genweb.upc.edu/svn/core/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['genweb'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'upc.genweb.banners',
          'plone.app.ldap',
#          'upc.remotecontrol',
#          'upcnet.simpleTask',
#          'upcnet.cas',
#          'Products.AJAXAddRemoveWidget',
#          'Products.PloneLDAP',
#          'Products.FCKeditor',
#          'Products.Ploneboard',
#          'Products.PloneFormGen',
          'Products.LinguaPlone',
#          'Products.Collage',
#          'Products.Poi',
#          'Products.PloneSurvey',
#          'Products.windowZ',
#          'Products.PlonePopoll',
#          'archetypes.schemaextender',
     
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
