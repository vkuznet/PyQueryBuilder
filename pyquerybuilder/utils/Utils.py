#!/usr/bin/env python

"""
This class reads sqlalchemy schema metadata in order to construct
joins for an arbitrary query.

Review all the foreign key links.
"""

__author__ = "Dong Liang <liangd@ihep.ac.cn>"
__revision__ = "$Revision: 1.11 $"

from yaml import load_all
from yaml import Loader
from sqlalchemy import Column
from operator import itemgetter

def pull_operator_side(clause, tables_of_concern):
    """
    add table into clause
    """
    if clause.__dict__.has_key('left'):
        if issubclass(clause.left.__class__, Column):
            tables_of_concern.add(clause.left.table)
    if clause.__dict__.has_key('right'):
        if issubclass(clause.right.__class__, Column):
            tables_of_concern.add(clause.right.table)

def load_file(filename):
    """load all datas from yamlfile"""
    ifile = open(filename, 'r')
    datas = []
    for data in load_all(ifile, Loader):
        datas.append(data)
    return datas

def weight_sort(adjlist):
    """
    [[node_idx, weight],[node_idx, weight], ...]
    """
    return adjlist.sort(key=itemgetter(1))

def similar(str1, str2):
    """
    similar means they:
      match if less than 3 character

      started as the same prefix 3 character
      ended with same suffix 3 character
         and left str are subset
    """
    str1 = str1.lower()
    str2 = str2.lower()
    minlen = min(len(str1), len(str2))
    larger = str2
    if len(str1) > len(str2):
        larger = str1
    sign = True
    for i in range(minlen):
        if (str1[i] != str2[i]):
            if i < 3:
                sign = False
            if not (str1[i:] in larger):
                sign = False
                break
    if sign == True:
        return sign
    for i in range(minlen):
        j = -i - 1
        if (str1[j] != str2[j]):
            if i < 3:
                return False
            if not (str1[:i-1] in larger):
                return False
    return True

