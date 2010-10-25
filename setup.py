#!/usr/bin/env python
import os
import sys

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages, Feature
from distutils.cmd import Command
from distutils.command.build_ext import build_ext
from distutils.errors import CCompilerError
from distutils.errors import DistutilsPlatformError, DistutilsExecError
from distutils.core import Extension
from distutils.command.install import INSTALL_SCHEMES
from pyquerybuilder import version

required_python_version = '2.6'
requirements = []
version      = version
readme       = open('doc/README', 'r').read()
name         = "PyQueryBuilder"
desc         = "A general purpose Query Builder over RDMS system"
keywords     = ["Query Language", "SQL", "RDMS", "databases"]
#scriptfiles  = filter(os.path.isfile, ['etc/web_service'])
data_files = [('config',['pyquerybuilder/config/ipythonrc']),
              ('map',['pyquerybuilder/tools/map.yaml'])],
packages     = find_packages()

#data_files   = [
#    ('src/doc', ['LICENSE', 'README']),
#]
package_data = {
    'pyquerybuilder': ['web/templates/*.tmpl', 'web/css/*.css', 
            'web/images/*', 'web/js/*.js','doc/*'],
}
classifiers = [
            "Development Status :: Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: BSD License",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX",
            "Programming Language :: Python",
            "Topic :: Database :: Web interface"]
author       = 'Valentin Kuznetsov, Andrew J. Dolgert, Liang Dong'
author_email = 'vkuznet@gmail.com, ajd27@cornell.edu, liangd@ihep.ac.cn'
url          = 'http://a.b.c'
license      = 'BSD'

def main():
    """Main routine"""
    if sys.version < required_python_version:
        s = "I'm sorry, but %s %s requires Python %s or later."
        print s % (name, version, required_python_version)
        sys.exit(1)

    # set default location for "data_files" to
    # platform specific "site-packages" location
    for scheme in INSTALL_SCHEMES.values():
        scheme['data'] = scheme['purelib']


    dist = setup(
      name                 = name,
      version              = version,
      description          = desc,
      long_description     = readme,
      keywords             = keywords,
#      package_dir          = {"":'pyquerybuilder'},
      packages             = packages,
      package_data         = package_data,
#      data_files           = data_files,
      include_package_data = True,
      install_requires     = requirements,
#      scripts              = scriptfiles,
      classifiers          = classifiers,
      author               = author,
      author_email         = author_email,
      url                  = url,
      license              = license,
     )
if __name__ == "__main__":
    main()


