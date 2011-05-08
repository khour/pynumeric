#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math

import pulp.constants
from pulp import LpVariable, LpProblem, lpSum, LpInteger

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


def divide(problem, non_int_index, l, A, b, c):
    """
    Возвращает 2 новые проблемы с модифицированными
    ограничениями на переменные
    """
    bounds = [{'low_bound' : var.lowBound, 'up_bound' : var.upBound}
              for var in problem.sortedVariables()]

    bounds_left = [bound.copy() for bound in bounds]
    bounds_right = [bound.copy() for bound in bounds]

    bounds_left[non_int_index]['up_bound'] = int(math.floor(l))
    bounds_right[non_int_index]['low_bound'] = int(math.floor(l) + 1)

    return (prepare_problem(A, b, c, bounds_left),
            prepare_problem(A, b, c, bounds_right))


def iteration(problems, r0, A, b, c):
    """Итерация метода ветвей и границ"""
    # Шаг 1: взять проблему из списка
    problem = problems.pop()

    # Шаг 2: решить проблему
    status = problem.solve()
    variables = problem.sortedVariables()

    # Если решения нет - возврат
    if not pulp.constants.LpStatus[status] == 'Optimal':
        return None

    cx = sum(var.varValue * ci for var, ci in zip(variables, c))

    # Если cx <= r0 - возврат, решение не оптимальное
    if cx <= r0:
        return None

    # Шаг 3: проверка решения на целочисленность. Если выполняется
    # условие целочисленности - возврат, решение оптимально
    non_int_index = calc_non_int_index(variables)
    if non_int_index is None:
        return variables, cx
    else:
        # Шаг 4: создать 2 новые проблемы, добавить в список
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
        res = iteration(problems, r0, A, b, c)     
        if res is not None:
            answer, r0 = res

    if answer is None:
        return None, None, None
    else:
        return ([x.varValue for x in answer],
                sum(xi.varValue * ci for xi, ci in zip(answer, c)),
                iteration_count)


def pulp_solve(A, b, c, bounds):
    problem = LpProblem(sense = pulp.constants.LpMaximize)

    x = [LpVariable('x' + str(i + 1),
                    bound['low_bound'],
                    bound['up_bound'],
                    LpInteger)
         for i, bound in enumerate(bounds)]

    problem += lpSum(ci * xi for ci, xi in zip(c, x))

    for ai, bi in zip(A, b):
        problem += lpSum(aij * xj for aij, xj in zip(ai, x)) == bi
    
    status = problem.solve()
    
    return (pulp.constants.LpStatus[status],
            [variable.varValue for variable in problem.sortedVariables()],
            problem.objective.value())


import sys
stdout = sys.stdout

f = open('BranchAndBound.txt', 'w+')

def test(msg, A, b, c, d_down, d_up):
    bounds = []
    for down_bound, up_bound in zip (d_down, d_up):
        bounds.append({'low_bound' : down_bound, 'up_bound' : up_bound})
        
    sys.stdout = f
    print '\n', msg,
    sys.stdout = stdout
    status, solution, cx = pulp_solve(A, b, c, bounds)
    if status == 'Optimal':
        sys.stdout = f
        result, cx, iteration_count = solve(A, b, c, bounds)
        print ':', iteration_count, 'iterations'
        print result
        print 'cx =', cx
        sys.stdout = stdout
    else:
        sys.stdout = f
        print '\nHas no solution'
        sys.stdout = stdout

# вариант 1
A = [
    [1,0,0,12,1,-3,4,-1],
    [0,1,0,11,12,3,5,3],
    [0,0,1,1,0,22,-2,1],
]

b = [40,107,61]
c = [2,1,-2,-1,4,-5,5,5]
d_down = [0,0,0,0,0,0,0,0]
d_up = [3,5,5,3,4,5,6,3]

test('1', A, b, c, d_down, d_up)

# вариант 2
A = [
    [1, -3, 2,  0,  1,  -1, 4,  -1, 0],
    [1, -1, 6,  1,  0,  -2, 2,  2,  0],
    [2, 2,  -1, 1,  0,  -3, 8,  -1, 1],
    [4, 1,  0,  0,  1,  -1, 0,  -1, 1],
    [1, 1,  1,  1,  1,  1,  1,  1,  1],
]

b = [3,9,9,5,9]
c = [-1,5,-2,4,3,1,2,8,3]
d_down = [0,0,0,0,0,0,0,0,0]
d_up = [5,5,5,5,5,5,5,5,5]

test('2', A, b, c, d_down, d_up)

# вариант 3
A = [
    [1,0,0,12,1,-3,4,-1,2.5,3],
    [0,1,0,11,12,3,5,3,4,5.1],
    [0,0,1,1,0,22,-2,1,6.1,7],
]

b = [43.5,107.3,106.3]
c = [2,1,-2,-1,4,-5,5,5,1,2]
d_down = [0,0,0,0,0,0,0,0,0,0]
d_up = [2,4,5,3,4,5,4,4,5,6]

test('3', A, b, c, d_down, d_up)

# вариант 4
A = [
    [4,0,0,0,0,-3,4,-1,2,3],
    [0,1,0,0,0,3,5,3,4,5],
    [0,0,1,0,0,22,-2,1,6,7],
    [0,0,0,1,0,6,-2,7,5,6],
    [0,0,0,0,1,5,5,1,6,7],
]

b = [8,5,4,7,8]
c = [2,1,-2,-1,4,-5,5,5,1,2]
d_down = [0,0,0,0,0,0,0,0,0,0]
d_up = [10,10,10,10,10,10,10,10,10,10]

test('4', A, b, c, d_down, d_up)

# вариант 5
A = [
    [1,-5,3,1,0,0],
    [4,-1,1,0,1,0],
    [2,4,2,0,0,1],
]

b = [-8,22,30]
c = [7,-2,6,0,5,2]
d_down = [2,1,0,0,1,1]
d_up = [6,6,5,2,4,6]

test('5', A, b, c, d_down, d_up)

# вариант 6
A = [
    [1,0,0,3,1,-3,4,-1],
    [0,1,0,4,-3,3,5,3],
    [0,0,1,1,0,2,-2,1],
]

b = [30,78,18]
c = [2,1,-2,-1,4,-5,5,5]
d_down = [0,0,0,0,0,0,0,0]
d_up = [5,5,3,5,6,7,7,8]

test('6', A, b, c, d_down, d_up)

# вариант 7
A = [
    [1, -3, 2,  0,  1,  -1,   4,  -1,  0],
    [1, -1, 6,  1,  0,  -2,   2,  2,   0],
    [2, 2,  -1, 1,  0,  -3,   2,  -1,  1],
    [4, 1,  0,  0,  1,  -1,   0,  -1,  1],
    [1, 1,  1,  1,  1,  1,    1,  1,   1],
]

b = [18,18,30,15,18]
c = [7,5,-2,4,3,1,2,8,3]
d_down = [0,0,0,0,0,0,0,0,0]
d_up = [8,8,8,8,8,8,8,8,8]

test('7', A, b, c, d_down, d_up)
    
# вариант 8
A = [
    [1,0,1,0,4,3,4],
    [0,1,2,0,55,3.5,5],
    [0,0,3,1,6,2,-2.5],
]

b = [26, 185, 32.5]
c = [1,2,3,-1,4,-5,6]
d_down = [0,1,0,0,0,0,0]
d_up = [1,2,5,7,8,4,2]

test('8', A, b, c, d_down, d_up)

# вариант 9
A = [
    [2,0,1,0,0,3,5],
    [0,2,2.1,0,0,3.5,5],
    [0,0,3,2,0,2,1.1],
    [0,0,3,0,2,2,-2.5],
]

b = [58,66.3,36.7,13.5]
c = [1,2,3,1,2,3,4]
d_down = [1,1,1,1,1,1,1]
d_up = [2,3,4,5,8,7,7]

test('9', A, b, c, d_down, d_up)

# вариант 10
A = [
    [1,0,0,1,1,-3,4,-1,3,3],
    [0,1,0,-2,1,1,7,3,4,5],
    [0,0,1,1,0,2,-2,1,-4,7],
]

b = [27,6,18]
c = [-2,1,-2,-1,8,-5,3,5,1,2]
d_down = [0,0,0,0,0,0,0,0,0,0]
d_up = [8,7,6,7,8,5,6,7,8,5]

test('10', A, b, c, d_down, d_up)

f.close()