"""cal minimal cost spanning tree"""
from heapq import heappush, heappop
from pyquerybuilder.qb.WGraph import RootedWGraph

def calmcst(keys, graph, lefts):
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
                    sum_weight = sum(infos[node]['weight'])
                    if (sum_weight, node) not in heap_out:
                        heappush(heap_out, (sum_weight, node))
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
                        sum_weight = sum(infos[adj]['weight'])
                        if (sum_weight, adj) not in heap_out:
                            heappush(heap_out, (sum_weight, adj))
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
            while True:
                if len(heap_out) != 0:
                    root = heappop(heap_out)
                else:
                    break
                if root[1] not in lefts:
                    return traceback(root, infos, keys)
#            root = heappop(heap_out)
#            if len(heap_out) != 0:
#                candi = heappop(heap_out)
#                if root[0] == candi[0]:
#                    raise Exception('Warnning: weight cofliction')
            return traceback(root, infos, keys)

def traceback(node, infos, keys):
    """traceback from root form a subtree"""
    root = node[1]
    subtree = [[] for _ in range(len(infos))]
    for idx in range(len(infos[root]['ancestor'])):
        while infos[root]['ancestor'][idx] != keys[idx]:
            subtree[root].append((infos[root]['ancestor'][idx], 0))
            root = infos[root]['ancestor'][idx]
        subtree[root].append((keys[idx], 0))
        root = node[1]
#    print subtree
    return RootedWGraph(subtree, root)

