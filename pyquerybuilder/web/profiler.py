#!/usr/bin/env python
#-*- coding: ISO-8859-1 -*-

"""
Profiler for Cherrpy web framework. Each api call will trigger
a new profile stats dump
"""

import os
import cProfile
import cherrypy

class CachegrindHandler(cherrypy.dispatch.LateParamPageHandler):
    """Callable which profiles the subsequent handlers and outputs cachegrind files."""

    def __init__(self, next_handler):
        self.next_handler = next_handler

    def __call__(self):
        """
        Profile this request and output results in a cachegrind compatible format.
        """

        try:
            p = cProfile.Profile()
            p.runctx('self._real_call()', globals(), locals())
        finally:
            count = 1
            filename = '/tmp/profile'
            path = cherrypy.request.path_info.strip("/").replace("/", "_")
            script = cherrypy.request.app.script_name.strip("/").replace("/", "_")
            path = path + "_" + script
            while not filename or os.path.exists(filename):
                filename = os.path.join('/tmp', "profile.out.%s_%d" % (path, count))
                count += 1
            print "writing profile output to %s" % filename
            p.dump_stats(filename)
        return self.result

    def _real_call(self):
        """Call the next handler and store its result."""
        self.result = self.next_handler()


def cachegrind():
    """A CherryPy 3 Tool for loading Profiling requests."""
    cherrypy.request.handler = CachegrindHandler(cherrypy.request.handler)
