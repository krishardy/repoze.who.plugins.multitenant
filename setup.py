from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='repoze.who.plugins.multitenant',
      version=version,
      description="A repoze.who/repoze.what plugin that supports user name + company name as a composite user identifer for multitenant applications",
      long_description="""\
repoze.who.plugins.multitenant is...

    * A plugin for repoze.who and repoze.what 1.x that
      allows the developer to build groupings of users
      within a "company".  The users are authenticated
      by the company name, user name and password.

    * This is primarily used in multitenant applications,
      where multiple companies will use the same
      application instance.  This is common in distributed
      business applications such as SalesForce.com.
""",
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Database :: Front-Ends',
        'Operating System :: OS Independent',
        'Environment :: Plugins'
        ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='repoze.who repoze.what auth acl',
      author='Kris Hardy',
      author_email='kris@rkrishardy.com',
      url='http://www.rkrishardy.com',
      license='BSD License',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
        'repoze.who',
        'repoze.what',
        'sqlalchemy>=0.7'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
