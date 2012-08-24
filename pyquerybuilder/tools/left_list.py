#!/usr/bin/env python

"""
This class reads left join dictionary
"""

__author__ = "Dong Liang <liangd@ihep.ac.cn>"
__revision__ = "$Revision: 1.11 $"

import os
from yaml import load_all
from yaml import Loader

def load_file(filename):
    """load all datas from yamlfile"""
    ifile = open(filename, 'r')
    datas = []
    for data in load_all(ifile, Loader):
        datas.append(data)
    return datas

def load_left_join(filename):
    """load left join list"""
    if os.path.isfile(filename):
        datas = load_file(filename)
        left_dict = datas[0]
        return left_dict['left']
    return []
