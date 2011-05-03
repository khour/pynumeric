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

# problem.solve()
# 
# print "Status:", LpStatus[problem.status]
# 
# for v in problem.variables():
#         print v.name, "=", v.varValue
# 
# print "Minimum cost =", value(problem.objective)

class Edge:
    def __init__(self, source, sink, cost, flow):
        self.source = source
        self.sink = sink
        self.cost = cost
        self.flow = flow
        
        
class Point:
    def __init__(self, name, data, phi=0):
        self.name = name
        self.data = data
        self.phi = phi
        self.marked = False


def find_basis_edge(point, edges):
    """Находит базисное ребро, включающее poing"""
    for edge in edges:
        if ((edge.source == point and edge.sink.marked) or (edge.sink == point and edge.source.marked)) and edge.flow > 0:
            return edge
    return None


def calculate_potentials(points, edges):
    """Вычисляет потенциалы"""
    for point in points:
        point.marked = False
        
    while not all([point.marked for point in points]):
        
        points[0].phi = 0
        points[0].marked = True
        
        for point in points[1:]:
            edge = find_basis_edge(point, edges)
            if edge is not None and not point.marked:
                if point is edge.sink:
                    point.phi = edge.source.phi - edge.cost
                else:
                    point.phi = edge.sink.phi + edge.cost
                point.marked = True
    
    for point in points:
        point.marked = False


def check(points, edges):
    """Проверка условия оптимальности решения"""
    for edge in edges:
        if edge.flow == 0:
            if edge.source.phi - edge.sink.phi - edge.cost > 0:
                return edge
    return None 


def find_cycle(nodes, edges):
    """Находит цикл в графе"""
    todo = nodes[:]
    EDGES = lambda node: [edge.sink for edge in edges if node is edge.source] + [edge.source for edge in edges if node is edge.sink]
    while todo:
        node = todo.pop()
        stack = [node]
        while stack:
            top = stack[-1]
            for node in EDGES(top):
                if node in stack:
                    if len(stack[stack.index(node):]) > 2:
                        return stack[stack.index(node):]
                if node in todo:
                    stack.append(node)
                    todo.remove(node)
                    break
            else:
                node = stack.pop()
    return None


def iteration(points, edges):
    """Итерация метода"""
    calculate_potentials(points, edges)

    edge_to_add = check(points, edges)
    if edge_to_add is None:
        return True

    temp_edges = [edge for edge in edges if edge.flow > 0] + [edge_to_add]
    hz = find_cycle(points, temp_edges)

    cycle = []
    for i, node1 in enumerate(hz[:-1]):
        for node2 in hz[i+1:]:
            for edge in temp_edges:
                if (edge.sink is node1 and edge.source is node2) or (edge.sink is node2 and edge.source is node1):
                    cycle.append(edge)
    
    Uplus, Uminus = [edge_to_add], []
    temp_edges = cycle[:]
    temp_edges.remove(edge_to_add)
    while temp_edges != []:
        for edge in temp_edges:
            if Uplus[-1].sink is edge.source or Uplus[-1].source is edge.sink:
                Uplus.append(edge)
                temp_edges.remove(edge)
                break
            else:
                if Uplus[-1].sink is edge.sink or Uplus[-1].source is edge.source:
                    Uminus.append(edge)
                    temp_edges.remove(edge)
                    break

    tetta = float('inf')
    for edge in Uminus:
        if tetta > edge.flow:
            tetta = edge.flow

    for edge in edges:
        if edge in Uplus:
            edge.flow += tetta
        if edge in Uminus:
            edge.flow -= tetta
    
    return False


points = [
    Point('1', 5),
    Point('2', -2),
    Point('3', 5),
    Point('4', -4),
    Point('5', -9),
    Point('6', 2),
    Point('7', 3)
]

edges = [
    Edge(points[0], points[1], 7, 2),
    Edge(points[0], points[2], 6, 3),
    Edge(points[0], points[4], 3, 0),
    Edge(points[1], points[2], 4, 0),
    Edge(points[1], points[5], 3, 0),
    Edge(points[2], points[3], 6, 4),
    Edge(points[2], points[4], 5, 4),
    Edge(points[3], points[5], 1, 0),
    Edge(points[4], points[3], 4, 0),
    Edge(points[4], points[5], -1, 0),
    Edge(points[5], points[6], 4, 2),
    Edge(points[6], points[0], 2, 0),
    Edge(points[6], points[4], 7, 5),
]


while True:
    if iteration(points, edges):
        break

for edge in edges:
    print 'Edge (%s, %s), flow = %d' % (edge.source.name, edge.sink.name, edge.flow)

print 'cx =', sum(edge.cost * edge.flow for edge in edges)
print 'Total flow =', sum(edge.flow for edge in edges)