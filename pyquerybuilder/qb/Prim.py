#from collections import defaultdict
from heapq import *

def prim(graph, nodes, root=None):
    """
    prim algorithm to gen a minial weighted spanning tree
    input:
           nodes: list of nodes on graph, could be subset of all nodes
           graph: [ [(adj1, weight), ...],
                    ...
                  ]
    return mst: [(n1, n2, cost), ...]
    """
#    conn = defaultdict(nodes)
    conn = {}
    for n1 in nodes:
        conn[n1] = []
        for n2, w in graph[n1]:
            conn[n1].append((w, n1, n2))

    mst = [ [] for _ in range(len(graph)) ]
#    mst = []
    if root == None:
        root = nodes[0]
    used = set( [root] )
    usable_edges = conn[root][:]
    heapify( usable_edges )

    while usable_edges:
        cost, n1, n2 = heappop( usable_edges )
        if n2 not in used:
            used.add( n2 )
#            mst.append((n1,n2,cost))
            mst[n1].append((n2, cost))
            mst[n2].append((n1, cost))

            for e in conn[ n2 ]:
                if e[ 2 ] not in used:
                    heappush( usable_edges, e )
    return mst

if __name__ == "__main__":
#test
    nodes = [0, 1, 2, 3, 4, 5, 6]
#    keys = [0, 2, 4, 6]
    root = 4
    graph = [ [(1, 7), (3, 5),],
          [(0, 7), (2, 8), (3, 9), (4, 7),],
          [(1, 8), (4, 5),],
          [(0, 5), (1, 9), (4, 15), (5, 6),],
          [(1, 7), (2, 5), (3, 15), (5, 8), (6, 9)],
          [(3, 6), (4, 8), (6, 11)],
          [(4, 8), (5, 9)],
        ]

    print "prim:", prim(graph, nodes, root=None)
