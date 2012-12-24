"""cal minimal cost spanning tree"""
#from logging import getLogger
#from heapq import heappush, heappop
from pyquerybuilder.qb.WGraph import RootedWGraph
from math import ceil
#_LOGGER = getLogger("ConstructQuery")

def calmcst(keys, graph):
    """
    Input: keys is the keywords set of a Query
    Output : minimal cost spanning tree, cover keys.

    Map keys onto entity nodes on schema graph
    S = Map(keys) are the nodes sets
    S is a subset of V_ent Union V_rel

    queue_bfs
    WatitQueue : for index missing cases
    roots : for candidate root
    infos  : list for appendix node information
             [   { iterator: -1,
                   ancestor:[node, node, ...],
                   weight:[x, y, ...]
                 }, ...
             ]
    iterator   : current steps
    """
#    print keys
#    print graph
    queue_bfs = []
    queue_wait = []
    length = len(graph)
    klen = len(keys)
    infos = [ {
#        'iterator': -1, \
               'ancestor':[None for _ in range(klen)], \
               'weight':[0 for _ in range(klen)] }\
              for _ in range(length)]

    roots = {}
    ceiling = length
    iterator = 0
    for idx in range(klen):
        source = keys[idx]
        queue_bfs.insert(0, (source, iterator))
# update source
        sou = infos[source]
        sou['ancestor'][idx] = source
#        sou['iterator'] = 0
    end_iterator = 1
    while iterator >= 0 and iterator < 100:
#        print "iterator ", iterator
#        print "queue bfs ", queue_bfs
        while len(queue_bfs) != 0 and iterator <= end_iterator:
#            if infos[queue_bfs[-1]]['iterator'] == iterator:
            if queue_bfs[-1][-1] == iterator:
#            explore( queue_bfs.pop() )
##### begin of explore
                node = queue_bfs.pop()[0]
#                print "node ", node

# ---------------result check------------------
                result_ready = True
                if end_iterator == iterator:
                    end_iterator = iterator + 1
# before explore node, check weather it's available as a result
                for ind in range(klen):
                    if infos[node]['ancestor'][ind] == None:
                        result_ready = False
# if result, put it in roots
                if result_ready:
                # calculate sum weight
                    wt = sum(infos[node]['weight'])
##                    wtc = ceil(wt)
##                    if wtc < ceiling:
##                        ceiling = wtc
##                    if wt <= ceiling:
##                        if not roots.has_key(node):
##                            roots[node] = wt
##                        elif roots[node] > wt:
                            #print node,wt,infos[node]
##                            roots[node] = wt
                    roots[node] = wt
                    if end_iterator > iterator:
                        end_iterator = iterator
# ---------------result check------------------
# explore each adjacent node
                for adj, wnp in graph[node]:
                    if wnp < 1:
#                        infos[adj]['iterator'] = iterator + 1
                        queue_bfs.insert(0, (adj, iterator + 1))
                    else:
#                        infos[adj]['iterator'] = iterator + 2
                        queue_wait.insert(0, (node, adj, wnp, iterator + 2))
                        continue # suspending visit node
                    for i in range(klen):
                        if infos[node]['ancestor'][i] != None:
                            if infos[adj]['ancestor'][i] == None:
#                                print node, " find ", adj, " on ", i
                                infos[adj]['ancestor'][i] = node
                                infos[adj]['weight'][i] = \
                                    infos[node]['weight'][i] + wnp
                            elif infos[adj]['weight'][i] > \
                                    infos[node]['weight'][i] + wnp:
#                                print node, " update ", adj, " on ", i
                                infos[adj]['weight'][i] = \
                                    infos[node]['weight'][i] + wnp
# ---------------result check------------------
                    result_ready = True
                    for ind in range(klen):
                        if infos[adj]['ancestor'][ind] == None:
                            result_ready = False
# if result, put it in roots
                    if result_ready:
                # calculate sum weight
                        wt = sum(infos[adj]['weight'])
##                        wtc = ceil(wt)
##                        if wtc < ceiling:
##                            ceiling = wtc
##                        if wt <= ceiling:
##                            if not roots.has_key(adj):
                                #print adj,wt,infos[adj]
##                                roots[adj] = wt
##                            elif roots[adj] > wt:
                                #print adj,wt,infos[adj]
##                                roots[adj] = wt
                        roots[adj] = wt
                        if end_iterator > iterator:
                            end_iterator = iterator
# ---------------result check------------------
##### end of explore
            else:
                break
        while len(queue_wait) != 0 and iterator <= end_iterator:
            ver, adj, wvp, itera = queue_wait[-1]
#            if infos[adj]['iterator'] == iterator:
            if itera == iterator:
            # explore suspended node
                for ind in range(klen):
                    if infos[ver]['ancestor'][ind] != None:
                        if infos[adj]['ancestor'][ind] == None:
                            infos[adj]['ancestor'][ind] = ver
                            infos[adj]['weight'][ind] = \
                                infos[ver]['weight'][ind] + wvp
                        elif infos[adj]['weight'][ind] > \
                                infos[ver]['weight'][ind] + wvp:
                        # update p.ancestor
                            infos[adj]['ancestor'][ind] = ver
                            infos[adj]['weight'][ind] = \
                                infos[ver]['weight'][ind] + wvp
                    # pass
                queue_wait.pop()
                queue_bfs.insert(0, (adj, itera + 1))
            else:
                break
        iterator = iterator + 1
        if len(roots) != 0:
            iterator = -1
            #print "iterator is ", iterator
            for root in roots:
                #print "root is ", root
                #import pdb
                #pdb.set_trace()
                subtree, wt = traceback(root, infos, keys)
                ##print "subtree is", subtree, wt
                wtc = ceil(wt)
                if wtc < ceiling:
                    ceiling = wtc
                if wt <= ceiling:
                    yield (subtree, roots[root])
#                yield (subtree, roots[root])

def check_including(li, anc):
    for l in li:
        if anc == l[0]:
            return True
    return False


def traceback(root, infos, keys):
    subtree = [[] for _ in range(len(infos))]
    sum_w = 0
    for idx in range(len(infos[root]['ancestor'])):
        croot = root
        adj = infos[croot]['ancestor'][idx]
        while adj != keys[idx]:
            if not check_including(subtree[croot], adj):
                ##print "add node,", croot, adj, "for",keys[idx]
                subtree[croot].append((adj, 0))
                sum_w += infos[croot]['weight'][idx] - infos[adj]['weight'][idx]
            #print "add node,", adj, croot, "for",keys[idx]
                subtree[adj].append((croot, 0))
            croot = adj
            adj = infos[croot]['ancestor'][idx]
        if not check_including(subtree[croot], adj):
            ##print "add node,", croot, keys[idx], "for",keys[idx]
            subtree[croot].append((keys[idx], 0))
            sum_w += infos[croot]['weight'][idx] - infos[keys[idx]]['weight'][idx]
        #print "add node,", keys[idx], croot, "for",keys[idx]
            subtree[keys[idx]].append((croot, 0))
    return RootedWGraph(subtree, root), sum_w
