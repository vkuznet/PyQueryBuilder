#!/usr/bin/env python

"""
This class reads sqlalchemy schema metadata in order to construct
joins for an arbitrary query.

Review all the foreign key links.
"""

__author__ = "Dong Liang <liangd@ihep.ac.cn>"
__revision__ = "$Revision: 1.11 $"

class LinkObj(object):
    """class encapsulate for foreign key"""
    def __init__(self, sqlalchemyfk=None):
        """initialize"""
        if sqlalchemyfk:
            self.name = sqlalchemyfk.name
            self.lcolumn = sqlalchemyfk.parent.name
            self.rcolumn = sqlalchemyfk.column.name
            self.ltable = sqlalchemyfk.parent.table.name
            self.rtable = sqlalchemyfk.column.table.name
            self.fkey = sqlalchemyfk
        else:
            self.name = ""
            self.lcolumn = ""
            self.rcolumn = ""
            self.ltable = ""
            self.rtable = ""

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and\
            self.name == other.name)

    def __ne__(self, other):
        return not self.__eq__(other)

    def set(self, name, ltable, rtable, lcolumn, rcolumn):
        """set LinkObj by table/columns"""
        self.name = name
        self.ltable = ltable
        self.rtable = rtable
        self.lcolumn = lcolumn
        self.rcolumn = rcolumn

class CLinkObj(object):
    """
    class encapsulate for complex link between two table
    It may be a composition of several foreignkey links or custormed
    links, but all the links must have exactly same ltable and rtable.
    """
    def __init__(self, foreignkeys=None, name=None):
        """initialize CLinkObj with name
            String  ltable        rtable
            list    lcolumn       rcolumn
        """
        self.name = name
        self.lcolumn = []
        self.rcolumn = []
        self.ltable = None
        self.rtable = None
        self.linklist = set()
        self.fks = foreignkeys
        if foreignkeys != None:
            for fks in foreignkeys:
                link = LinkObj(fks)
                if self.ltable == None:
                    self.ltable = link.ltable
                    self.rtable = link.rtable
                if self.ltable != link.ltable or self.rtable != link.rtable:
                    raise Exception("""conflict on links, different direction
                    or more than three table involving.""")
                self.lcolumn.append(link.lcolumn)
                self.rcolumn.append(link.rcolumn)
                self.linklist.add(link)
        self.weight = 0
        self.indexed = 1

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and\
            self.name == other.name)

    def __ne__(self, other):
        return not self.__eq__(other)

    def set(self, name, links):
        """set CLinkObj by LinkObjs"""
        self.name = name
        for link in links:
            self.ltable = link.ltable
            self.rtable = link.rtable
            if self.ltable != link.ltable or self.rtable != link.rtable:
                raise Exception("""conflict on links, different direction
                or more than three table involving.""")
            self.lcolumn.append(link.lcolumn)
            self.rcolumn.append(link.rcolumn)
        self.linklist = links

