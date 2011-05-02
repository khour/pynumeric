#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math

import pulp.constants
from pulp import LpVariable, LpProblem, lpSum

ZERO = 1e-6

LpProblem.sortedVariables = lambda self: sorted(
                                self.variables(),
                                key = lambda x: int(x.name[1:]))


def calc_non_int_index(variables):
    """Возвращает индекс первой нецелой переменной решения"""
    for i, var in enumerate(variables):
        value = var.varValue
        if abs(value - round(value)) > ZERO:
            return i
    return None


def prepare_problem(A, b, c, bounds):
    """
    Создаёт проблемы по заданным матрице A, вектору b,
    оптимизируемой функции и ограничениям на переменные
    """
    problem = LpProblem(sense = pulp.constants.LpMaximize)

    x = [LpVariable('x' + str(i + 1), bound['low_bound'], bound['up_bound'])
         for i, bound in enumerate(bounds)]

    problem += lpSum(ci * xi for ci, xi in zip(c, x))

    for ai, bi in zip(A, b):
        problem += lpSum(aij * xj for aij, xj in zip(ai, x)) == bi

    return problem


def divide(problem, non_zero_index, l, A, b, c):
    """
    Возвращает 2 новые проблемы с модифицированными
    ограничениями на переменные
    """
    bounds = [{'low_bound' : var.lowBound, 'up_bound' : var.upBound}
              for var in problem.sortedVariables()]

    bounds_left = [bound.copy() for bound in bounds]
    bounds_right = [bound.copy() for bound in bounds]

    bounds_left[non_zero_index]['up_bound'] = int(math.floor(l))
    bounds_right[non_zero_index]['low_bound'] = int(math.floor(l) + 1)

    return (prepare_problem(A, b, c, bounds_left),
            prepare_problem(A, b, c, bounds_right))


def iteration(problems, r0, A, b, c):
    """Итерация метода ветвей и границ"""
    # Шаг 1: взять проблему из списка
    problem = problems.pop()

    # Шаг 2: решить проблему
    status = problem.solve()
    variables = problem.sortedVariables()

    print '\nVariables:'
    for var in variables:
        print '%s: (%d, %d), value = %f' % (var.name, var.lowBound,
                                            var.upBound, var.varValue)

    # Если решения нет - возврат
    if not pulp.constants.LpStatus[status] == 'Optimal':
        print 'Not optimal'
        return None

    cx = sum(var.varValue * ci for var, ci in zip(variables, c))
    print '\ncx =', cx

    # Если cx <= r0 - возврат, решение не оптимальное
    if cx <= r0:
        print 'cx <= r0'
        return None

    # Шаг 3: проверка решения на целочисленность. Если выполняется
    # условие целочисленности - возврат, решение оптимально
    non_int_index = calc_non_int_index(variables)
    if non_int_index is None:
        print 'Optimal solution'
        return variables, r0
    else:
        # Шаг 4: создать 2 новые проблемы, добавить в список
        print 'Divide'
        l = variables[non_int_index].varValue
        problems.extend(divide(problem, non_int_index, l, A, b, c))
        return None


def solve(A, b, c, bounds):
    """Решает проблему методом ветвей и границ"""
    problems = [prepare_problem(A, b, c, bounds)]
    iteration_count = 0
    answer = None
    r0 = 0

    while (problems != []):
        iteration_count += 1
        print '\n\n        Iteration %s...\n' % iteration_count
        res = iteration(problems, r0, A, b, c)
        if res is not None:
            answer, r0 = res

    if answer is None:
        print '\nNo solution'
    else:
        print '\nHas solution:'

        for xi in answer:
            print xi.name, '=', xi.varValue

        cx = sum(xi.varValue * ci for xi, ci in zip(answer, c))
        print '\ncx =', cx



A = [
    [1, -3, 2,  0,  1,  -1,   4,  -1,  0],
    [1, -1, 6,  1,  0,  -2,   2,  2,   0],
    [2, 2,  -1, 1,  0,  -3,   2,  -1,  1],
    [4, 1,  0,  0,  1,  -1,   0,  -1,  1],
    [1, 1,  1,  1,  1,  1,    1,  1,   1],
]

b = [
    18,
    18,
    30,
    15,
    18,
]

c = [
    7,
    5,
    -2,
    4,
    3,
    1,
    2,
    8,
    3,
]

bounds = [
    {'low_bound' : 0, 'up_bound' : 8},
    {'low_bound' : 0, 'up_bound' : 8},
    {'low_bound' : 0, 'up_bound' : 8},
    {'low_bound' : 0, 'up_bound' : 8},
    {'low_bound' : 0, 'up_bound' : 8},
    {'low_bound' : 0, 'up_bound' : 8},
    {'low_bound' : 0, 'up_bound' : 8},
    {'low_bound' : 0, 'up_bound' : 8},
    {'low_bound' : 0, 'up_bound' : 8},
]

solve(A, b, c, bounds)

