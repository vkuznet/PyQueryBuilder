import math

MAX = 65536

def shift(lis):
    n = 0
    for x in lis:
        n += 1 << x
    return n

def get_D(C, m):
    """return all subsets of C, which has m elements"""
    n = len(C)
    for i in comb(C, m):
        yield i

def get_E(D):
    """
    return all subsets of D
    which has D[0], but not a copy of D
    """
    yield [D[0]]
    for i in comb(D[1:], len(D) - 2):
        yield [D[0]] + i

def comb(items, n=None):
    """return combination of items"""
    if n is None:
        n = len(items)
    for i in range(len(items)):
        v = items[i:i+1]
        if n == 1:
            yield v
        else:
            rest = items[i+1:]
            for c in comb(rest, n-1):
                yield v + c

def steiner(G, K, d, PT):
    """
    len(K) > 3
    return steiner tree ST
    ST taking K as terminal sets
    ST ensure its the minimal Spanning Tree
    currently G is limited to 62 nodes (see 1 << n issue in python)
    """
    if len(K) <= 1:
        return None
    n = len(G)
    q = K[0]
    C = K[1:]
    n = len(G)
    S = {}
    P = {}
    def check(key):
        """initailize S for key"""
        if not S.has_key(key):
            S[key] = [MAX]*n
        if not P.has_key(key):
            P[key] = [set([])]*n

    for t in C:# initailize S for {t}
        for j in range(n):
            key = 1 << t
            check(key)
            S[key][j] = d[t][j]
            P[key][j] = PT[t][j]
#    print "Y is ", K
#    print "q is ", q
#    print "C is ", C
    for m in range(2, len(K)):
#        print "m is", m
        # enumerate D
        for D in get_D(C, m):
#            print "D is", D
            for i in range(n):
                key = shift(D)
                check(key)
                S[key][i] = MAX
#                print "S %s %s is %d" %(i, str(D), MAX)
            for j in range(n):
                u = MAX
                _p = -1
                cp = None
                for E in get_E(D):
#                    print "E is", E
                    key1 = shift(E)
                    key2 = shift(D) - shift(E)
                    check(key1)
                    check(key2)
                    if u > S[key1][j] + S[key2][j]:
                        u = S[key1][j] + S[key2][j]
                        _p = j
                        cp = P[key1][j].union(P[key2][j])
                for i in range(n):
                    key = shift(D)
                    check(key)
                    if S[key][i] > d[i][j] + u:
                        S[key][i] = d[i][j] + u
                        P[key][i] = PT[i][j].union(cp)
#                        print "S %s %s is %d" %(i, str(D), d[i][j]+u)
    v = MAX
    f = None
    fj = 0
    fp = None
    for j in range(n):
        u = MAX
        _p = -1
        cp = None
        for E in get_E(C):
            key1 = shift(E)
            key2 = shift(C) - shift(E)
            if u > S[key1][j] + S[key2][j]:
                u = S[key1][j] + S[key2][j]
                _p = j
                cp = P[key1][j].union(P[key2][j])
        if v > d[q][j] + u:
            v = d[q][j] + u
            f = cp.union(PT[q][j])
            fj = j
            fp = cp
    for key in S:
        nk = []
        res = 0
        if key > 0:
            res = 2**int(math.log(key, 2))
        else:
            continue
        while res > 0:
            if key | res == key:
                nk.append(str(int(math.log(res, 2))))
            res  = res >> 1
    return f, fj
