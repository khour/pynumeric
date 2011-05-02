#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

def find_path(capacity, path, source, sink, flow):
    if source == sink:
        return flow

    path[source] = True
    for i, v in enumerate(path):
        if not v and capacity[source][i] > 0:
            df = find_path(capacity, path, i, sink, min(flow, capacity[source][i]))
            if df > 0:
                capacity[source][i] -= df
                capacity[i][source] += df
                return df
    return 0


def max_flow(capacity, source, sink):
    flow = 0
    while True:
        path = [False for i in xrange(len(capacity))]
        df = find_path(capacity, path, source, sink, sys.maxint)
        flow += df
        if df == 0:
            return flow


capacity = [
#   [s, 1, 2, 3, 4, 5, 6, 7, t]
    [0, 0, 0, 0, 4, 6, 2, 0, 0], # s
    [3, 0, 2, 0, 7, 0, 4, 0, 0], # 1
    [0, 0, 0, 0, 0, 0, 0, 0, 0], # 2
    [0, 3, 5, 0, 2, 0, 4, 0, 2], # 3
    [0, 0, 0, 0, 0, 1, 0, 0, 0], # 4
    [0, 0, 0, 0, 0, 0, 0, 0, 7], # 5
    [0, 0, 0, 0, 0, 1, 0, 0, 0], # 6
    [0, 0, 3, 6, 0, 0, 4, 0, 1], # 7
    [0, 0, 1, 0, 0, 0, 0, 0, 0], # t
]

print max_flow(capacity, 0, 8)

