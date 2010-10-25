#!/usr/bin/env python
#-*- coding: ISO-8859-1 -*-
##########################################################################
#  Copyright (C) 2008 Valentin Kuznetsov <vkuznet@gmail.com>
#  All rights reserved.
#  Distributed under the terms of the BSD License.  The full license is in
#  the file doc/LICENSE, distributed as part of this software.
##########################################################################
"""
Common utilities
"""
import time

# Python Cookbook
def fetchsome(cursor, arraysize=10):
    """A generator that simplifies the use of fetchmany"""
    while True:
        results = cursor.fetchmany(arraysize)
        if not results: 
            break
        for result in results:
            yield result

def fetch_from_to(cursor, i_limit=10, i_offset=0):
    """A way to retrieve a limited number of rows"""
#    if i_offset:
#       for i in xrange(0,i_offset):
#           cursor.next()
    results = cursor.fetchmany(i_limit)
    if not results: 
        return
    for result in results:
        yield result

def swap_dict(original_dict):
    """swap dictionary"""
    return dict([(v, k) for (k, v) in original_dict.iteritems()])

def elementwise(function):
    """
    if arg is a Sequence then the result is a sequence of fn(elem)
    otherwise result is fn(arg)
    """
    def newfn(arg):
        """inner function of elementwise"""
        if hasattr(arg,'__getitem__'):  # is a Sequence
            return type(arg)(map(function, arg))
        else:
            return function(arg)
    return newfn

@elementwise
def item_len(item):
    """return length of the string format of item""" 
    return len(str(item))

def make_time(intime):
    """formatted time into %a, %d %b %Y %H:%M:%S GMT """
    return time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(long(intime)))

