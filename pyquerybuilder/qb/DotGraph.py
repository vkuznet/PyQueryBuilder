#!/usr/bin/env python
"""
Writes a graph in a format for graphviz's dot program to make an image.
"""
__author__ = "Andrew J. Dolgert <ajd27@cornell.edu>"
__revision__ = "$Revision: 1.1 $"

class DotGraph(object):
    """ dot graph used to make an image"""
    def __init__(self, file_obj):
        """name used for specification, output is a file"""
        self.name = "G"
        self.edges = []
        self.out = file_obj

    def set_name(self, name):
        """set name"""
        self.name = name

    def add_edge(self, start, finish):
        """add edge"""
        self.edges.append((start, finish))

    def finish_output(self):
        """output to file"""
        print >> self.out, "digraph %s {" % (self.name)
        for edge in self.edges:
            print >> self.out, "	%s -> %s;" % (edge)
        print >> self.out, "}"
