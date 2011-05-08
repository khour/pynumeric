#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pulp.constants
from pulp import LpVariable, LpProblem, lpSum, LpInteger

class Edge:
    def __init__(self, source, sink, cost, flow):
        self.source = nodes_dict[source]
        self.sink = nodes_dict[sink]
        self.cost = cost
        self.flow = flow
        
        
class Node:
    def __init__(self, name, data, phi=0):
        self.name = name
        self.data = data
        self.phi = phi
        self.marked = False


def find_basis_edge(node, edges):
    """Находит базисное ребро, включающее poing"""
    for edge in edges:
        if (((edge.source == node and edge.sink.marked) or
             (edge.sink == node and edge.source.marked))
            and edge.flow > 0):
            return edge
    return None


def calculate_potentials(nodes, edges):
    """Вычисляет потенциалы"""
    for node in nodes:
        node.marked = False
        
    while not all([node.marked for node in nodes]):
        
        nodes[0].phi = 0
        nodes[0].marked = True
        
        for node in nodes[1:]:
            edge = find_basis_edge(node, edges)
            if edge is not None and not node.marked:
                if node is edge.sink:
                    node.phi = edge.source.phi - edge.cost
                else:
                    node.phi = edge.sink.phi + edge.cost
                node.marked = True
    
    for node in nodes:
        node.marked = False


def check(edges):
    """Проверка условия оптимальности решения"""
    for edge in edges:
        if edge.flow == 0:
            if edge.source.phi - edge.sink.phi - edge.cost > 0:
                return edge
    return None 


def find_cycle(nodes, edges):
    """Находит цикл в графе"""
    todo = nodes[:]
    EDGES = lambda node: ([edge.sink for edge in edges
                                     if node is edge.source] +
                          [edge.source for edge in edges
                                       if node is edge.sink])
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


def iteration(nodes, edges):
    """Итерация метода"""
    # Подсчитать потенциалы
    calculate_potentials(nodes, edges)
    # print 'Potentials:'
    # for node in nodes:
    #     print 'u(%s) = %d' % (node.name, node.phi)

    # Проверить оценки
    edge_to_add = check(edges)
    if edge_to_add is None:
        return True
    
    # print '\ndelta(%s %s) > 0, ' % (edge_to_add.source.name,
    #                                 edge_to_add.sink.name),
    # print '(i0 j0) = (%s %s)' % (edge_to_add.source.name,
    #                              edge_to_add.sink.name)

    # Найти цикл
    
    temp_edges = [edge for edge in edges if edge.flow > 0] + [edge_to_add]
    hz = find_cycle(nodes, temp_edges)    
    cycle = []
    for i, node1 in enumerate(hz[:-1]):
        for node2 in hz[i+1:]:
            for edge in temp_edges:
                if ((edge.sink is node1 and edge.source is node2) or
                    (edge.sink is node2 and edge.source is node1)):
                    cycle.append(edge)

    # Раскидать цикл по U+, U-
    Uplus, Uminus = [edge_to_add], []
    temp_edges = cycle[:]
    temp_edges.remove(edge_to_add)
    while temp_edges != []:
        for edge in temp_edges:
            done = False
            for plus_edge in Uplus:
                if (plus_edge.sink is edge.source or
                    plus_edge.source is edge.sink):
                    Uplus.append(edge)
                    temp_edges.remove(edge)
                    done = True
                    break
                else:
                    if (plus_edge.sink is edge.sink or
                        plus_edge.source is edge.source):
                        Uminus.append(edge)
                        temp_edges.remove(edge)
                        done = True
                        break
            if done:
                break

            for minus_edge in Uminus:
                if (minus_edge.sink is edge.source or
                    minus_edge.source is edge.sink):
                    Uminus.append(edge)
                    temp_edges.remove(edge)
                    done = True
                    break
                else:
                    if (minus_edge.sink is edge.sink or
                        minus_edge.source is edge.source):
                        Uplus.append(edge)
                        temp_edges.remove(edge)
                        done = True
                        break
            if done:
                break
    # print 'Uplus: { ',
    # for edge in Uplus:
    #     print '(%s, %s) ' % (edge.source.name, edge.sink.name),
    # print '}'
    # print 'Uminus: { ',
    # for edge in Uminus:
    #     print '(%s, %s) ' % (edge.source.name, edge.sink.name),
    # print '}'
    
    # Найти минимальное значение потока в U-    
    tetta = float('inf')
    for edge in Uminus:
        if tetta > edge.flow:
            tetta = edge.flow
    
    # print '\nTetta = %d' % tetta

    # Преобразовать поток
    for edge in edges:
        if edge in Uplus:
            edge.flow += tetta
        if edge in Uminus:
            edge.flow -= tetta
    
    # print '\nNew plan:'
    # for edge in edges:
    #     if edge.flow > 0:
    #         print 'x(%s, %s) = %d' % (edge.source.name,
    #                                   edge.sink.name,
    #                                   edge.flow)
    # print '\nNew basis:\n{ ',
    # for edge in edges:
    #     if edge.flow > 0:
    #         print '(%s, %s) ' % (edge.source.name, edge.sink.name),
    # print '}' 
    
    return False

def solve(nodes, edges):
    iteration_count = 1
    while True:
        if iteration(nodes, edges):
            break
        iteration_count += 1
    
    return edges, iteration_count
    print

"""
def pulp_solve(nodes, edges):
    problem = LpProblem(sense = pulp.constants.LpMinimize)
    arcs = []
    for edge in edges:
        arcs.append((edge.source.name, edge.sink.name))
    
    variables = LpVariable.dicts("Route", arcs, None, None, LpInteger)

    problem += lpSum(variables[arc] for edge, arc in zip(edges, arcs))

    problem += lpSum(ci * xi for ci, xi in zip(c, x))

    for ai, bi in zip(A, b):
        problem += lpSum(aij * xj for aij, xj in zip(ai, x)) == bi
    
    status = problem.solve()
    
    return (pulp.constants.LpStatus[status],
            [variable.varValue for variable in problem.sortedVariables()],
            problem.objective.value())
"""

import sys
stdout = sys.stdout

f = open('MinimumCost.txt', 'w+')

def test(msg, nodes, edges):
    sys.stdout = f
    print '\n', msg,
    sys.stdout = stdout
    solution_edges, iteration_count = solve(nodes, edges)
    sys.stdout = f
    print ':', iteration_count, 'iterations'
    for edge in solution_edges:
        print 'X%s%s = %d,' % (edge.source.name,
                                            edge.sink.name,
                                            edge.flow),

    print '\ncx =', sum(edge.cost * edge.flow for edge in solution_edges)
    sys.stdout = stdout


# вариант 1
nodes = [
    Node('1', 9),
    Node('2', 5),
    Node('3', -4),
    Node('4', -3),
    Node('5', -6),
    Node('6', 2),
    Node('7', 2),
    Node('8', -7),
    Node('9', 2),
]

nodes_dict = {}
for node in nodes:
    nodes_dict[node.name] = node

edges = [
    Edge('1', '2', 9, 2),
    Edge('1', '8', 5, 7),
    Edge('2', '3', 1, 4),
    Edge('2', '6', 3, 0),
    Edge('2', '7', 5, 3),
    Edge('3', '9', -2, 0),
    Edge('4', '3', -3, 0),
    Edge('5', '4', 6, 3),
    Edge('6', '5', 8, 4),
    Edge('7', '3', -1, 0),
    Edge('7', '4', 4, 0),
    Edge('7', '5', 7, 5),
    Edge('7', '9', 1, 0),
    Edge('8', '7', 2, 0),
    Edge('8', '9', 2, 0),
    Edge('9', '6', 6, 2),
]

test('1', nodes, edges)

# вариант 2, неполное условие
nodes = [
    Node('1', 5),
    Node('2', -5),
    Node('3', -1),
    Node('4', -6),
    Node('5', -1),
    Node('6', -6),
    Node('7', 3),
    Node('8', 11),
]

nodes_dict = {}
for node in nodes:
    nodes_dict[node.name] = node

edges = [
    Edge('1', '2', 8, 5),
    Edge('1', '8', 3, 0),
    Edge('2', '3', 2, 0),
    Edge('2', '7', 9, 0),
    Edge('3', '6', 4, 3),
    Edge('4', '3', -2, 0),
    Edge('4', '6', 1, 0),
    Edge('5', '4', 8, 6),
    Edge('6', '5', 4, 0),
    Edge('7', '3', 11, 4),
    Edge('7', '5', 6, 7),
    Edge('7', '6', 2, 0),
    Edge('8', '6', 5, 3),
    Edge('8', '7', 5, 8),
]

# test('2', nodes, edges)

# вариант 3
nodes = [
    Node('1', 9),
    Node('2', -2),
    Node('3', -4),
    Node('4', -6),
    Node('5', -1),
    Node('6', 4),
    Node('7', 4),
    Node('8', -4),
]

nodes_dict = {}
for node in nodes:
    nodes_dict[node.name] = node

edges = [
    Edge('1', '2', 8, 5),
    Edge('1', '8', 3, 4),
    Edge('2', '3', 2, 0),
    Edge('2', '7', 9, 3),
    Edge('3', '6', 4, 0),
    Edge('4', '3', -2, 0),
    Edge('5', '4', -3, 6),
    Edge('6', '5', 8, 7),
    Edge('7', '3', 13, 4),
    Edge('7', '4', 1, 0),
    Edge('7', '5', 1, 0),
    Edge('7', '6', 7, 3),
    Edge('8', '6', -1, 0),
    Edge('8', '7', 1, 0),
]

test('3', nodes, edges)

# вариант 4
nodes = [
    Node('1', 3),
    Node('2', 2),
    Node('3', -6),
    Node('4', -7),
    Node('5', 9),
    Node('6', -5),
    Node('7', 4),
]

nodes_dict = {}
for node in nodes:
    nodes_dict[node.name] = node

edges = [
    Edge('1', '2', 1, 0),
    Edge('1', '7', 4, 3),
    Edge('2', '3', 5, 2),
    Edge('2', '5', 3, 0),
    Edge('3', '4', 3, 0),
    Edge('3', '6', 2, 0),
    Edge('5', '3', 10, 4),
    Edge('5', '4', 5, 7),
    Edge('5', '6', 2, 0),
    Edge('6', '4', 1, 0),
    Edge('7', '5', 8, 2),
    Edge('7', '6', 6, 5),
]

test('4', nodes, edges)

# вариант 5
nodes = [
    Node('1', 6),
    Node('2', 4),
    Node('3', -1),
    Node('4', -2),
    Node('5', -2),
    Node('6', 1),
    Node('7', -6),
]

nodes_dict = {}
for node in nodes:
    nodes_dict[node.name] = node

edges = [
    Edge('1', '2', 3, 0),
    Edge('1', '5', 5, 2),
    Edge('1', '6', 4, 4),
    Edge('1', '7', 2, 0),
    Edge('2', '3', 5, 3),
    Edge('2', '5', -1, 0),
    Edge('2', '7', 7, 1),
    Edge('3', '4', 6, 2),
    Edge('3', '7', 1, 0),
    Edge('4', '6', 1, 0),
    Edge('5', '3', 2, 0),
    Edge('5', '4', -2, 0),
    Edge('5', '6', 1, 0),
    Edge('6', '7', 7, 5),
]

test('5', nodes, edges)

# вариант 6
nodes = [
    Node('1', 2),
    Node('2', -4),
    Node('3', 6),
    Node('4', -2),
    Node('5', 2),
    Node('6', 0),
    Node('7', 1),
    Node('8', -5),
]

nodes_dict = {}
for node in nodes:
    nodes_dict[node.name] = node

edges = [
    Edge('1', '2', 6, 2),
    Edge('1', '6', 2, 0),
    Edge('1', '7', -2, 0),
    Edge('2', '3', 3, 0),
    Edge('2', '4', 6, 2),
    Edge('2', '6', 1, 0),
    Edge('3', '5', 3, 0),
    Edge('3', '6', 4, 6),
    Edge('4', '3', -1, 0),
    Edge('4', '8', 1, 0),
    Edge('5', '8', 7, 5),
    Edge('6', '5', 5, 3),
    Edge('6', '7', 5, 3),
    Edge('6', '8', 3, 0),
    Edge('7', '2', 4, 4),
    Edge('7', '5', 2, 0),
    Edge('7', '8', 2, 0),
]

test('6', nodes, edges)

# вариант 7
nodes = [
    Node('1', 5),
    Node('2', -2),
    Node('3', 5),
    Node('4', -4),
    Node('5', -9),
    Node('6', 2),
    Node('7', 3),
]

nodes_dict = {}
for node in nodes:
    nodes_dict[node.name] = node

edges = [
    Edge('1', '2', 7, 2),
    Edge('1', '3', 6, 3),
    Edge('1', '5', 3, 0),
    Edge('2', '3', 4, 0),
    Edge('2', '6', 3, 0),
    Edge('3', '4', 6, 4),
    Edge('3', '5', 5, 4),
    Edge('4', '6', 1, 0),
    Edge('5', '4', 4, 0),
    Edge('5', '6', -1, 0),
    Edge('6', '7', 4, 2),
    Edge('7', '1', 2, 0),
    Edge('7', '5', 7, 5),
]

test('7', nodes, edges)

# вариант 8
nodes = [
    Node('1', 6),
    Node('2', 1),
    Node('3', 1),
    Node('4', -6),
    Node('5', -3),
    Node('6', 1),
]

nodes_dict = {}
for node in nodes:
    nodes_dict[node.name] = node

edges = [
    Edge('1', '2', 5, 4),
    Edge('1', '5', 1, 0),
    Edge('1', '6', 5, 2),
    Edge('2', '4', 10, 5),
    Edge('2', '6', 3, 0),
    Edge('3', '1', 1, 0),
    Edge('3', '2', 3, 0),
    Edge('3', '4', 6, 1),
    Edge('3', '5', 2, 0),
    Edge('4', '5', 3, 0),
    Edge('6', '4', 2, 0),
    Edge('6', '5', 4, 3),
]

test('8', nodes, edges)

f.close()