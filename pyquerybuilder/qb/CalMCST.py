"""cal minimal cost spanning tree"""
#from logging import getLogger
from heapq import heappush, heappop
from pyquerybuilder.qb.WGraph import RootedWGraph
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
    heap_out : for output the minimal cost option
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
    infos = [ {
#        'iterator': -1, \
               'ancestor':[None for _ in range(len(keys))], \
               'weight':[0 for _ in range(len(keys))] }\
              for _ in range(length)]

    heap_out = []
    iterator = 0
    for idx in range(len(keys)):
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
                for ind in range(len(keys)):
                    if infos[node]['ancestor'][ind] == None:
                        result_ready = False
# if result, put it in heap_out, sort as SUM of ['weight']
                if result_ready:
                # calculate sum weight
                    subgraph = traceback(node, infos, keys, graph)
                    sum_weight = subgraph.sum_weight()
                    if (sum_weight, subgraph) not in heap_out:
                        heappush(heap_out, (sum_weight, subgraph))
#                        print "heap update ", heap_out
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
                    for i in range(len(keys)):
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
                    for ind in range(len(keys)):
                        if infos[adj]['ancestor'][ind] == None:
                            result_ready = False
# if result, put it in heap_out, sort as SUM of ['weight']
                    if result_ready:
                # calculate sum weight
                        subgraph = traceback(adj, infos, keys, graph)
                        sum_weight = subgraph.sum_weight()
                        if (sum_weight, subgraph) not in heap_out:
                            heappush(heap_out, (sum_weight, subgraph))
#                            print "heap update ", heap_out
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
                for ind in range(len(keys)):
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
        if len(heap_out) != 0:
            sum_weights, subgraph = heappop(heap_out)
            return sum_weights, subgraph
#            if len(heap_out) != 0:
#                candi = heappop(heap_out)
#                if root[0] == candi[0]:
#                    raise Exception('Warnning: weight cofliction')
#            return traceback(root, infos, keys)

def get_weight(graph, i, j):
    """return graph[i][j]"""
    for edge in graph[i]:
        if edge[0] == j:
            return edge[1]

def check_including(li, anc):
    for l in li:
        if anc == l[0]:
            return True
    return False

def traceback(node, infos, keys, graph):
    """traceback from root form a subtree"""
    root = node
    subtree = [[] for _ in range(len(infos))]
    for idx in range(len(infos[root]['ancestor'])):
        anc = infos[root]['ancestor'][idx]
        while anc != keys[idx]:
            if not check_including(subtree[root], anc):
                #print root, anc, get_weight(graph, root, anc)
                wt = get_weight(graph, root, anc)
                subtree[root].append((anc, wt))
                subtree[anc].append((root, wt))
            root = anc
            anc = infos[root]['ancestor'][idx]
        anc = infos[root]['ancestor'][idx]
        #print keys[idx], anc, get_weight(graph, root, anc)
        if root != anc:
            wt = get_weight(graph, root, anc)
            subtree[root].append((keys[idx], wt))
            subtree[keys[idx]].append((root, wt))
        root = node
#    print subtree
#    _LOGGER.debug(subtree)
    return RootedWGraph(subtree, root)
