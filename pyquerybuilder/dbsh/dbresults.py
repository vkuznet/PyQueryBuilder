#!/usr/bin/env python
#-*- coding: ISO-8859-1 -*-
##########################################################################
#  Copyright (C) 2008 Valentin Kuznetsov <vkuznet@gmail.com>
#  All rights reserved.
#  Distributed under the terms of the BSD License.  The full license is in
#  the file doc/LICENSE, distributed as part of this software.
##########################################################################
"""SQL query results"""

class Results(object):
  """
  results with set operation
  query / title / values
  """
  def __init__(self):
      self.query = None
      self.titles= None
      self.values= None
  def set(self, result):
      self.query, self.titles, self.values = result
