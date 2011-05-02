#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pulp import *


nodes = [
    '1',
    '2',
    '3',
    '4',
    '5',
    '6',
    '7',
]

node_data = {
    '1' : 5,
    '2' : -2,
    '3' : 5,
    '4' : -4,
    '5' : -9,
    '6' : 2,
    '7' : 3,
}

routes = [
    ('1', '2'),
    ('1', '3'),
    ('1', '5'),
    ('2', '3'),
    ('2', '6'),
    ('3', '4'),
    ('3', '5'),
    ('4', '6'),
    ('5', '4'),
    ('5', '6'),
    ('6', '7'),
    ('7', '1'),
    ('7', '5'),
]

costs = {
    ('1', '2') : 7,
    ('1', '3') : 6,
    ('1', '5') : 3,
    ('2', '3') : 4,
    ('2', '6') : 3,
    ('3', '4') : 6,
    ('3', '5') : 5,
    ('4', '6') : 1,
    ('5', '4') : 4,
    ('5', '6') : -1,
    ('6', '7') : 4,
    ('7', '1') : 2,
    ('7', '5') : 7,
}

variables = LpVariable.dicts("Route", routes, 0, None, LpInteger)

problem = LpProblem('', LpMinimize)

problem += lpSum([variables[route] * costs[route] for route in routes])

for n in nodes:
    problem += lpSum(variables[(i, j)] for (i, j) in routes if i == n) - lpSum(variables[(i, j)] for (i, j) in routes if j == n) == node_data[n]

problem.solve()

print "Status:", LpStatus[problem.status]

for v in problem.variables():
        print v.name, "=", v.varValue

print "Minimum cost =", value(problem.objective)
