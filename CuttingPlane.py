#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import time

import pulp.constants
from pulp import LpVariable, LpProblem, lpSum, LpInteger

from numpy import matrix

ZERO = 1e-6
MAX_ITERATIONS_COUNT = 100

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


def trim_problem(A, b, variables, artifitial_j_list, c):
    """Убирает лишние переменные и ограничения"""
    if artifitial_j_list == []:
        return A, b, variables
        
    j = artifitial_j_list[0]
    
    original_A_length = len(A) - (len(variables) - len(c))
    row_index = len(A) + j - len(variables)
    
    row = [aij / A[row_index][j] for aij in A[row_index]]
    for i, next_row in enumerate(A[row_index + 1 :]):
        edited_row = [aij_next - aij_prev * next_row[j]
                      for aij_next, aij_prev in zip(next_row, row)]
        A[row_index + 1 + i] = edited_row
        b[row_index + 1 + i] -= b[row_index] * next_row[j]
    
    A = [[el for i, el in enumerate(row) if i != j] for row in A]
    A = A[:row_index] + A[row_index + 1:]
    b = b[:row_index] + b[row_index + 1:]
    
    artifitial_j_list.remove(j)
    artifitial_j_list = [j - 1 for j in artifitial_j_list]
    variables = variables[:j] + variables[j + 1:]
    
    return trim_problem(A, b, variables, artifitial_j_list, c)


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
    variables = problem.sortedVariables()

    # Шаг 2: убрать лишние переменные и ограничения
    j_list = [j for j, var in enumerate(variables) if var.varValue > ZERO]
    artifitial_j_list = [j for j in j_list if j >= len(c)]
    if artifitial_j_list != []:
        A, b, variables = trim_problem(A, b, variables, artifitial_j_list, c)
        # return None, A, b

    # Шаг 3: проверка решения на целочисленность
    x_list = [var.varValue for var in variables]
    if all(is_int(x) for x in x_list[:len(c)]):
        return x_list[:len(c)], A, b

    # Шаг 4: сформировать ограничение
    # вычислить базисные индексы
    j_list = [j for j, var in enumerate(variables) if var.varValue > ZERO]
    # построить базисную матрицу
    basis_matrix = [[aij for j, aij in enumerate(aj) if j in j_list]
                         for aj in A]
    B = matrix(basis_matrix).getI()

    j0 = calc_j0_index(variables, j_list)
    
    # единичный вектор :D
    e = matrix(map(lambda i: 0 if i != j0 else 1,
                   xrange(len(j_list)))).getT()

    y = (e.getT() * B).getT()
    alpha = (y.getT() * matrix(A)).tolist()[0]
    beta = (y.getT() * matrix(b).getT()).item()

    # Шаг 5: добавить ограничение
    A = update_A_matrix(A, alpha)
    b = update_b_vector(b, beta)
    
    return None, A, b

def solve(A, b, c):
    """Решает проблему методом Гомори"""
    iteration_count = 1
    x_list = None

    while x_list is None and iteration_count < MAX_ITERATIONS_COUNT:
        x_list, A, b = iteration(A, b, c)
        iteration_count += 1
    
    if x_list is None:
        return None, None, iteration_count
    else:
        return (x_list,
                sum(ci * xi for ci, xi in zip(c, x_list)),
                iteration_count)


def pulp_solve(A, b, c):
    problem = LpProblem(sense = pulp.constants.LpMaximize)

    x = [LpVariable('x' + str(i + 1),
                    0,
                    None,
                    LpInteger)
         for i in xrange(len(c))]

    problem += lpSum(ci * xi for ci, xi in zip(c, x))

    for ai, bi in zip(A, b):
        problem += lpSum(aij * xj for aij, xj in zip(ai, x)) == bi
    
    status = problem.solve()
    
    return (pulp.constants.LpStatus[status],
            [variable.varValue for variable in problem.sortedVariables()],
            problem.objective.value())

import sys
stdout = sys.stdout

f = open('CuttingPlane.txt', 'w+')

def test(msg, A, b, c):
    sys.stdout = f
    print '\n', msg,
    sys.stdout = stdout
    status, solution, cx = pulp_solve(A, b, c)
    if status == 'Optimal':
        x_list, cx, iteration_count = solve(A, b, c)
        sys.stdout = f
        print ':', iteration_count, 'iterations'
        print x_list
        print 'cx =', cx
        sys.stdout = stdout
    else:
        sys.stdout = f
        print '\nHas no solution'
        sys.stdout = stdout

# вариант 1
A = [
    [1,-5,3,1,0,0],
    [4,-1,1,0,1,0],
    [2,4,2,0,0,1],
]

b = [-8,22,30]
c = [7,-2,6,0,5,2]

test('1', A, b, c)

# вариант 2, не считает
A = [
    [1,-3,2,0,1,-1,4,-1,0],
    [1,-1,6,1,0,-2,2,2,0],
    [2,2,-1,1,0,-3,8,-1,1],
    [4,1,0,0,1,-1,0,-1,1],
    [1,1,1,1,1,1,1,1,1],
]

b = [3,9,9,5,9]
c = [-1,5,-2,4,3,1,2,8,3]

test('2', A, b, c)

# вариант 3
A = [
    [1, 0,  0,  12, 1,  -3, 4,  -1],
    [0, 1,  0,  11, 12, 3,  5,  3],
    [0, 0,  1,  1,  0,  22, -2, 1],
]

b = [40,107,61]
c = [2,1,-2,-1,4,-5,5,5]

test('3', A, b, c)

# вариант 4, не считает
A = [
    [1,2,3,12,1,-3,4,-1,2,3],
    [0,2,0,11,12,3,5,3,4,5],
    [0,0,2,1,0,22,-2,1,6,7],
]

b = [153,123,112]
c = [2,1,-2,-1,4,-5,5,5,1,2]

test('4', A, b, c)

# вариант 5
A = [
    [2,1,-1,-3,4,7],
    [0,1,1,1,2,4],
    [6,-3,-2,1,1,1],
]

b = [7,16,6]
c = [1,2,1,-1,2,3]

test('5', A, b, c)

# вариант 6
A = [
    [0,7,1,-1,-4,2,4],
    [5,1,4,3,-5,2,1],
    [2,0,3,1,0,1,5],
]

b = [12,27,19]
c = [10,2,1,7,6,3,1]

test('6', A, b, c)

# вариант 7
A = [
    [0,7,-8,-1,5,2,1],
    [3,2,1,-3,-1,1,0],
    [1,5,3,-1,-2,1,0],
    [1,1,1,1,1,1,1],
]

b = [6,3,7,7]
c = [2,9,3,5,1,2,4]

test('7', A, b, c)

# вариант 8
A = [
    [1,0,-1,3,-2,0,1],
    [0,2,1,-1,0,3,-1],
    [1,2,1,4,2,1,1],
]

b = [4,8,24]
c = [-1,-3,-7,0,-4,0,-1]

test('8', A, b, c)

# вариант 9
A = [
    [1,-3,2,0,1,-1,4,-1,0],
    [1,-1,6,1,0,-2,2,2,0],
    [2,2,-1,1,0,-3,2,-1,1],
    [4,1,0,0,1,-1,0,-1,1],
    [1,1,1,1,1,1,1,1,1],
]

b = [3,9,9,5,9]
c = [-1,5,-2,4,3,1,2,8,3]

test('9', A, b, c)

f.close()