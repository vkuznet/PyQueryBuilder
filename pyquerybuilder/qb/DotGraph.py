#!/usr/bin/env python
"""
Writes a graph in a format for graphviz's dot program to make an image.
"""
__author__ = "Andrew J. Dolgert <ajd27@cornell.edu>"
__revision__ = "$Revision: 1.1 $"

class MultiDot(object):
    """ multiple dot graph"""
    def __init__(self, file_name):
        """ base name """
        self.base_name = file_name
        self.dot_list = []

    def get_dot(self):
        """get a dot instance"""
        filename = "%s_%d.dot" % (self.base_name, len(self.dot_list))
        newfile = open(filename, 'w')
        self.dot_list.append(DotGraph(newfile))
        return self.dot_list[-1]

    def close_all(self):
        """ close all file """
        for dot in self.dot_list:
            dot.out.close()



class DotGraph(object):
    """ dot graph used to make an image"""
    def __init__(self, file_obj, name="G"):
        """name used for specification, output is a file"""
        self.name = name
        self.edges = []
        self.out = file_obj

    def set_name(self, name):
        """set name"""
        self.name = name

    def add_edge(self, start, finish, weight=None):
        """add edge"""
        if weight:
            self.edges.append((start, finish, float(weight)))
        else:
            self.edges.append((start, finish))

    def finish_output(self):
        """output to file"""
        print >> self.out, "digraph %s {" % (self.name)
        for edge in self.edges:
            if len(edge) == 2:
                print >> self.out, "	%s -> %s;" % (edge)
            if len(edge) == 3:
                print >> self.out, '    %s -> %s[label = "%.3f"];' % (edge)
        print >> self.out, "}"
