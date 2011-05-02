#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import time

import pulp.constants
from pulp import LpVariable, LpProblem, lpSum

from numpy import matrix

ZERO = 1e-6
MAX_ITERATIONS_COUNT = 50
MAX_RESTRICTIONS_COUNT = 30

LpProblem.sortedVariables = lambda self: sorted(
                                self.variables(),
                                key = lambda x: int(x.name[1:]))


def calc_j0_index(variables, j_list):

    try:
        return next((i, j) for i, j in enumerate(j_list) \
                           if not is_int(variables[j].varValue))[0]
    except StopIteration:
        return None


def is_int(value):
    """Проверка значения на целочисленность"""
    return abs(round(value) - value) <= ZERO


def update_A_matrix(A, alpha):
    """Обновляет матрицу ограничений A"""
    # добавить нули в новый столбец
    for row in A:
        row.append(0)

    # добавить новую строку с единицей в новом столбце
    new_row = map(lambda x: 0 if is_int(x)
                              else math.floor(x) - x, alpha)
    new_row.append(1)
    A.append(new_row)
    return A


def update_b_vector(b, beta):
    """Обновляет вектор b"""
    b.append(0 if is_int(beta) else math.floor(beta) - beta)
    return b


def trim_problem(A, b, variables, artifitial_j_list):
    """Убирает лишние переменные и ограничения"""
    offset = 3
    artifitial_j_list = [j - offset for j in artifitial_j_list]
    for j in artifitial_j_list:
        j_col = j + offset
        row = [aij / A[j][j_col] for aij in A[j]]
        for i, next_row in enumerate(A[j + 1 :]):
            A[j + 1 + i] = [aij_next - aij_prev * next_row[j_col]
                            for aij_next, aij_prev in zip(next_row, row)]

    new_A = []
    for i, row in enumerate(A):
        if i not in artifitial_j_list:
            new_A.append([aij for j, aij in enumerate(row)
                              if j - offset not in artifitial_j_list])

    new_b = [bj for i, bj in enumerate(b) if i not in artifitial_j_list]
    new_variables = [var for j, var in enumerate(variables)
                         if j - offset not in artifitial_j_list]

    return new_A, new_b, new_variables


def prepare_problem(A, b, c):
    """
    Создаёт проблемы по заданным матрице A,
    вектору b и оптимизируемой функции
    """
    problem = LpProblem(sense = pulp.constants.LpMaximize)

    x_list = [LpVariable("x" + str(i + 1), 0) for i in xrange(len(A[0]))]

    problem += lpSum(ci * xi for ci, xi in zip(c, x_list))

    for aj, bj in zip(A, b):
        problem += lpSum([aij * xi for aij, xi in zip(aj, x_list)]) == bj

    return problem


def iteration(A, b, c):
    """Итерация метода Гомори"""
    problem = prepare_problem(A, b, c)

    # Шаг 1: решить задачу ЛП
    status = problem.solve()
    print pulp.constants.LpStatus[status]

    variables = problem.sortedVariables()

    print
    for var in variables:
        print var.name, '=', var.varValue

    # Шаг 2: убрать лишние переменные и ограничения
    if len(A) >= MAX_RESTRICTIONS_COUNT:
        j_list = [j for j, var in enumerate(variables)
                    if var.varValue > ZERO]
        artifitial_j_list = [j for j in j_list if j >= len(A)]
        A, b, variables = trim_problem(A, b, variables, artifitial_j_list)
        # return None, A, b

    # Шаг 3: проверка решения на целочисленность
    x_list = [var.varValue for var in variables]
    if all(is_int(x) for x in x_list):
        print 'Integer solution'
        return x_list[:len(c)], A, b
    else:
        print 'Not integer solution'

    # Шаг 4: сформировать ограничение
    # вычислить базисные индексы
    j_list = [j for j, var in enumerate(variables) if var.varValue > ZERO]
    print '\nBasis indexes:\n', j_list

    # построить базисную матрицу
    basis_matrix = [[aij for j, aij in enumerate(aj) if j in j_list]
                         for aj in A]
    B = matrix(basis_matrix).getI()
    print '\nInverted basis matrix:\n', B

    j0 = calc_j0_index(variables, j_list)
    # единичный вектор :D
    e = matrix(map(lambda i: 0 if i != j0 else 1,
                   xrange(len(j_list)))).getT()
    print '\ne:\n', e

    y = (e.getT() * B).getT()
    print '\ny:\n', y

    alpha = (y.getT() * matrix(A)).tolist()[0]
    print '\nalpha:\n', alpha

    beta = (y.getT() * matrix(b).getT()).item()
    print '\nbeta:\n', beta

    # Шаг 5: добавить ограничение
    A = update_A_matrix(A, alpha)
    b = update_b_vector(b, beta)

    print '\nA:\n', matrix(A)
    print '\nb:\n', matrix(b).getT()

    return None, A, b

def solve(A, b, c):
    """Решает проблему методом Гомори"""
    iteration_count = 1
    x_list = None

    while x_list is None and iteration_count < MAX_ITERATIONS_COUNT:
        print '\n\n        Iteration %s...\n' % iteration_count
        x_list, A, b = iteration(A, b, c)
        iteration_count += 1

    print '\nResult solution:\n', x_list
    print 'cx =', sum(ci * xi for ci, xi in zip(c, x_list))


A = [
    [0, 7,  -8, -1, 5,  2,  1],
    [3, 2,  1,  -3, -1, 1,  0],
    [1, 5,  3,  -1, -2, 1,  0],
    [1, 1,  1,  1,  1,  1,  1],
]

b = [
    6,
    3,
    7,
    7,
]

c = [
    2,
    9,
    3,
    5,
    1,
    2,
    4,
]

solve(A, b, c)

