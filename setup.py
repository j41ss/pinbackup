#from distutils.core import setup
from setuptools import setup
setup(name='pinbackup',
      version='1.0',
      description='Pinterest backup tool',
      author='Peter G.',
      author_email='guileone@ukr.net',
      license='BSD License',
      install_requires= [ 'pycurl', 'colorama', ],
      entry_points= {
            'console_scripts':
              ['pbackup = pinbackup.paccess:main' ]
      },
      packages= [ 'pinbackup' ],
      )