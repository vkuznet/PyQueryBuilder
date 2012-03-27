"""
Node class is used to represent all the table node on schema
By Node class we could have virtual Node(aliased Table) and virtual
links.
Union-Find is applied on Node object.
"""

class Node(object):
    """class encapsulate node to represent a table on schema graph"""
    def __init__(self, name, cons=None):
        """initializing"""
        self.name = name
        self.parent = None
        self.rank = 0
        #self.inlinks = set()
        self.outlinks = {}
        self.table = None
        if cons != None:
            for con in cons:
                self.outlinks[con.name] = con

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.name == other.name)

    def __ne__(self, other):
        return not self.__eq__(other)

    def set_table(self, table):
        """set sqlalchemy table"""
        self.table = table

def make_set(node):
    """make set for a node"""
    node.parent = node
    node.rank = 0

def find(node):
    """
    Find the UFSet of given node by return the root of this UFSet
    With path compression
    """
    if node.parent != node:
        node.parent = find(node.parent)
    return node.parent

def union(node1, node2):
    """
    Union the UFSet of node1 & node2
    With Union by rank
    """
    node1_root = find(node1)
    node2_root = find(node2)
    if node1_root == node2_root:
        return
    if node1_root.rank < node2_root.rank:
        node1_root.parent = node2_root
    elif node2_root.rank > node2_root.rank:
        node2_root.parent = node1_root
    else:
        node2_root.parent = node1_root
        node1_root.rank = node1_root.rank + 1

# connectivity check
# 1. make_set for each node
# 2. traverse each fkcons, union(left,right)
# 3. travel each node then will know how many set left.
