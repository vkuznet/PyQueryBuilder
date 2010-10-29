'''Disttest library
This software is under the MIT license.
Copyright (c) 2010 Jared Forsyth

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Author: Jared Forsyth <jared@jaredforsyth.com>

usage:

## example setup.py

from disttest import test

setup(
    ...
    cmdclass = {'test': test},
    options = {
        'test': {
            'test_dir':['tests'], 
         # will add all test suite from  Test*.py files in the tests/ directory
        }
    },
)
'''

from distutils.core import Command
from distutils.errors import DistutilsOptionError
from distutils.fancy_getopt import longopt_xlate
#import string
import sys
from unittest import TestLoader, main

UNINITIALIZED = object()

class test(Command):

    """Command to run unit tests after in-place build"""

    description = "run unit tests after in-place build"

    user_options = [
        ('test-type=', 't', 'Which test type to use (e.g. py.test, unittest)'),
    ]
    test_commands = {}

    def initialize_options(self):
        """Set default values for all the options that this command supports. 
        Note that these defaults may be overridden by other commands, by the 
        setup script, by config files, or by the command-line."""
        self.test_type = 'py.test'
        for (_, _, _, _, options) in self.test_commands.values():
            for option in options:
                name = str.translate(option[0], longopt_xlate).rstrip('=')
                setattr(self, name, UNINITIALIZED)

    @classmethod
    def add_type(cls, name, options=(), required=None, \
                              defaults=None, validate=None):
        """support multiple type of testsuite
           it will modified the user_options in class attribute
           fill the test_commands with a specific function, options as well
           currently two type was considered
           py.test
           unittest
        """
        if defaults is None:
            defaults = {}
        for option in options:
            cls.user_options.append(option)
        def meta(function):
            """return function with setting test_commands"""
            cls.test_commands[name] = \
                 function, required, defaults, validate, options
        return meta

    def finalize_options(self):
        """Set final values for all the options that this command supports. 
        This is always called as late as possible, ie. after any option assign-
        ments from the command-line or from other commands have been done.
        """
        if self.test_type not in self.test_commands:
            raise DistutilsOptionError('invalid test_type')
        
        function, required, defaults, validate, options = \
                          self.test_commands[self.test_type]
        if validate is not None:
            validate(self)
        else:
            for option in options:
                name = str.translate(option[0], longopt_xlate).rstrip('=')
                value = getattr(self, name,)
                if value is UNINITIALIZED:
                    if name in defaults:
                        setattr(self, name, defaults[name])
                    elif required is None or name in required:
                        raise DistutilsOptionError( \
                              'Required option not given: %s' % option[0])

    def with_project_on_sys_path(self, func):
        """
        update sys path within current build env
        """
        self.run_command('build')
        cmd = self.get_finalized_command('build_py')

        old_path = sys.path[:]
        old_modules = sys.modules.copy()

        from os.path import normpath as normalize_path
  
        try:
            sys.path.insert(0, normalize_path(cmd.build_lib))
            func()
        finally:
            sys.path[:] = old_path
            sys.modules.clear()
            sys.modules.update(old_modules)

    def run(self):
        """run test"""
        self.with_project_on_sys_path(self.run_tests)

    def run_tests(self):
        """using test_commands switch to diff test type"""
        self.test_commands[self.test_type][0](self)

def make_onetest(function):
    """make test by executing?"""
    def meta(self):
        """transform func"""
        return function()
    return meta

def make_testcase(name, functions):
    """
    make testcase from functions list, by add them in to a testSuite
    """
    import unittest
    suite = unittest.TestSuite()
    cls = type(name, (unittest.TestCase,), {})
    for fnc in functions:
        real = make_onetest(fnc)
        setattr(cls, fnc.__name__, real)
        suite.addTest(cls(fnc.__name__))
    return suite

import os

@test.add_type('py.test', options=(
    ('test-dir=', 'd', 'Direcotry in which to search for tests'),
    ('test-recursive', 'r', 'Search recursively'),
    ), defaults={'test_recursive':False})
def run_py_test(tester):
    """run py test or run unittest
       unittest was loaded in this way:
       move to test dir
       get __import__('Test**.py') 
       if the module has suite function
       then TestSuite.addTest(module.suite())"""
    try:
        import py
    except ImportError:
        py = None

    import glob
    if type(tester.test_dir) == str:
        tester.test_dir = [tester.test_dir]

    test_files = []
    test_dirs = []

    def add_dir(direc):
        """explore directory and add Test**.py file in test_files"""
        for item in os.listdir(direc):
            full = os.path.join(direc, item)
            if os.path.isdir(full) and tester.test_recursive:
                add_dir(full)
#            elif os.path.isfile(full) and full.endswith('.py'):
            elif os.path.isfile(full) and full.endswith('.py') \
                                      and item.startswith('Test'):
                test_files.append(full)
                test_dirs.append(direc)

    for dire in tester.test_dir:
        fulldir = os.path.abspath(dire)
        add_dir(fulldir)

    if py:
        py.test.cmdline.main(test_files)
    else:
        print 'py.test not found. falling back to unittest. ' + \
               'For more informative errors, install py.test'
        import unittest
        suite = unittest.TestSuite()
        for indexs in range(0, len(test_files)):
            filen = test_files[indexs]
            dirn = test_dirs[indexs]
            os.chdir(dirn)
            mod = get_pyfile(filen)
            if mod.__dict__.has_key('suite'):
                suite.addTest(mod.suite())

        my_suite = unittest.TextTestRunner(verbosity=2)
        my_suite.run(suite)

def get_pyfile(fname):
    """import pyfile from __import__"""
    if sys.path[0] != os.path.dirname(fname):
        sys.path.insert(0, os.path.dirname(fname))
    mod = __import__(os.path.basename(fname)[:-3], None, None, ['__doc__'])
    return mod

def validate_unittest(tester): 
    """validate unittest using in finalize_options"""
    import unittest
    if tester.test_suite is None:
        if tester.test_modules is None:
            raise DistutilsOptionError(
                "You must specify a module or a suite"
            )
        tester.test_suite = self.test_module + ".test_suite"
    elif tester.test_module:
        raise DistutilsOptionError(
            "You may specify a module or a suite, but not both"
        )

@test.add_type('unittest', options=(
        ('test-module=', 'm', "Run 'test_suite' in specified module"),
        ('test-suite=', 's',
            "Test suite to run (e.g. 'some_module.test_suite')"),
    ), validate=validate_unittest)
def run_unittest(tester):
    """run unittest"""
    import unittest
    unittest.main(
        None, None, [unittest.__file__, tester.test_suite],
        testLoader = unittest.TestLoader()
    )

