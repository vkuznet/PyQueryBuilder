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
    createdate <--> creationdate
    moddate <--> lastmodificationdate
    type <--> datset_access_types
    anyway this could be replaced by a explicit configuration
    such as: dataset.type : DSTYPE.NAME via link from DATASET.TYPE
    """
    str1 = str1.lower()
    str2 = str2.lower()
    if len(str1) > len(str2):
        return str_including(str2, str1, 1)
    else:
        return str_including(str1, str2, 1)

def char_contains(str1, str2):
    """
    check whether str2 cotains all characters of str1
    """
    if set(str1).issubset(set(str2)):
        return True
    return False

def str_including(str1, str2, ecount=1):
    """
    figure out whether str1 is substring of str2,
    ecount is the number of mismatch characters
    """
    len1 = len(str1)
    len2 = len(str2)
    idx1 = 0
    idx2 = 0
    sign = True # matching
    stop = [] # last match
    while(idx1 < len1 and idx2 < len2):
        if str1[idx1] == str2[idx2]:# move both
            idx1 += 1
            idx2 += 1
            stop.append(idx2)
        else:# move till str2 end
            idx2 += 1
    if idx1 != len1:
        sign = False
    if sign == False and ecount > 0:# see idx1 move
        ecount -= 1
        for idx in reversed(range(len(stop))):
            if stop[idx] == len2:
                continue
            idx1 = idx + 2
            if str_including(str1[idx1:], str2[stop[idx]:], ecount):
                sign = True
                break
    return sign

def contain_link(jlinks, jtable, links):
    """check whether links are already in jlinks"""
    if not jlinks.has_key(jtable):
        return False
    answer = False
    for jlink in jlinks[jtable]:
        if len(jlink[0]) == len(links):
            for idx in range(len(jlink[0])):
                if jlink[0][idx].rtable == links[idx].rtable and \
                    jlink[0][idx].ltable == links[idx].ltable and \
                    jlink[0][idx].lcolumn == links[idx].lcolumn and \
                    jlink[0][idx].rcolumn == links[idx].rcolumn:
                    answer = True
                else:
                    answer = False
                    break
    return answer
