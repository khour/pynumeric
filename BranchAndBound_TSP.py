#!/usr/bin/env python
# -*- coding: utf-8 -*-

from HungarianAlgorithm import HungarianAlgorithm
import copy

INF = float('inf')


def print_indexes(indexes, costs):
    total = 0
    for row, column in indexes:
        value = costs[row][column]
        total += value
    
    i, j = indexes[0]
    print i + 1,
    indexes = indexes[1:]
    while indexes != []:
        for i_next, j_next in indexes:
            if i_next == j:
                i, j = i_next, j_next
                print '->', i + 1,
                indexes.remove((i_next, j_next))
                break
    print '->', j + 1

    print 'Total cost =', total


def find_cycle(starting_index, indexes):
    """
    Найти первый цикл, начинающийся со starting_index и
    состоящий из элементов в indexes
    """
    cycle = [starting_index]
    indexes = indexes[:]

    while indexes != []:
        last_cycle_index = cycle[-1]

        for index in indexes:
            if last_cycle_index[1] == index[0]:
                cycle.append(index)
                indexes.remove(index)
                break

        if last_cycle_index == cycle[-1]:
            break

    return cycle


def is_one_cycle(indexes):
    """Проверяет, является ли набор indexes одним циклом"""
    cycle = find_cycle(indexes[0], indexes[1:])

    if len(cycle) == len(indexes) and cycle[0][0] == cycle[-1][1]:
        return True

    return False


def find_shortest_subcycle(indexes):
    """Находит самый короткий подцикл в indexes"""
    min_cycle = indexes[:]
    for index in indexes:
        temp_indexes = indexes[:]
        temp_indexes.remove(index)
        cycle = find_cycle(index, temp_indexes)

        if len(cycle) < len(min_cycle):
            min_cycle = cycle

    return min_cycle


def iteration(problems, min_cost):
    """Итерация метода"""
    # Шаг 1, взять проблему из списка
    problem = problems.pop()

    # Шаг 2, решить проблему, сравнить с минимальной оценкой
    indexes, iteration_count = HungarianAlgorithm().solve(problem)
    total = sum(problem[x][y] for x, y in indexes)

    if total < min_cost:
        # Шаг 3, проверить, является ли одним циклом. Если да - возврат
        if is_one_cycle(indexes):
            return total, find_cycle(indexes[0], indexes[1:])

        # Шаг 4, выбрать подцикл с наименьшим числом дуг, сформировать
        # на основе него новые проблемы, добавить в список
        else:
            sub_cycle = find_shortest_subcycle(indexes)
            for index in sub_cycle:
                new_problem = copy.deepcopy(problem)
                new_problem[index[0]][index[1]] = INF
                problems.append(new_problem)

    return None


def solve(problem):
    """
    Решает проблему, переданную в problem,
    методом исключения подциклов
    """
    problems = [problem]
    min_cost = INF
    min_indexes = []
    itercount = 1

    while problems != []:
        res = iteration(problems, min_cost)

        if res is not None:
            min_cost, min_indexes = res

        itercount += 1

    return min_cost, min_indexes, itercount


import sys
stdout = sys.stdout

f = open('BranchAndBound_TSP.txt', 'w+')

def test(msg, costs):
    sys.stdout = f
    print '\n', msg,
    sys.stdout = stdout
    min_cost, min_indexes, itercount = solve(costs)
    sys.stdout = f
    print ':', itercount, 'iterations'
    print_indexes(min_indexes, costs)
    sys.stdout = stdout


# вариант 1
costs = [
    [INF,10,25,25,10],
    [1,INF,10,15,2],
    [8,9,INF,20,10],
    [14,10,24,INF,15],
    [10,8,25,27,INF],
]

test('1', costs)

# вариант 2
costs = [
    [INF,10,10,8,13,1],
    [3,INF,1,17,17,7],
    [1,10,INF,6,1,17],
    [6,3,2,INF,5,12],
    [8,17,8,13,INF,11],
    [11,14,12,6,11,INF],
]

test('2', costs)

# вариант 3
costs = [
    [INF,8,0,1,18,16,5],
    [19,INF,12,5,11,8,17],
    [10,19,INF,17,11,15,5],
    [1,8,9,INF,11,2,2],
    [11,12,14,8,INF,4,1],
    [9,3,5,17,15,INF,19],
    [13,6,15,13,18,10,INF],
]

test('3', costs)

# вариант 4
costs = [
    [INF,   18,     13,     18,     8,      16,     11,     0],
    [0,     INF,    1,      8,      2,      15,     19,     11],
    [1,     10,     INF,    18,     5,      15,     12,     12],
    [15,    16,     10,     INF,    16,     10,     6,      9],
    [2,     18,     14,     16,     INF,    18,     13,     1],
    [5,     19,     1,      19,     1,      INF,    7,      4],
    [5,     7,      16,     0,      0,      8,      INF,    6],
    [10,    8,      13,     10,     12,     3,      13,     INF],
]

test('4', costs)

# вариант 5
costs = [
    [INF,13,2,17,14],
    [11,INF,11,8,2],
    [4,10,INF,3,6],
    [9,4,6,INF,19],
    [3,7,12,18,INF],
]

test('5', costs)

# вариант 6
costs = [
    [INF,6,16,16,4,12,11,1,4,10],
    [1,INF,16,9,17,5,3,2,6,19],
    [19,4,INF,11,17,8,10,4,15,11],
    [7,1,17,INF,17,2,5,6,10,17],
    [8,18,18,13,INF,0,19,6,12,14],
    [3,5,13,19,16,INF,12,17,2,19],
    [1,4,1,18,2,17,INF,8,12,10],
    [6,14,19,7,19,19,10,INF,2,9],
    [2,14,18,0,16,17,13,15,INF,1],
    [1,12,2,6,19,4,13,7,0,INF],
]

test('6', costs)

# вариант 7
costs = [
    [INF,12,11,1,18,4,14,3,18],
    [9,INF,14,12,7,10,4,18,9],
    [7,8,INF,18,1,6,1,9,19],
    [10,18,0,INF,3,14,3,11,4],
    [7,3,17,10,INF,14,14,9,8],
    [17,16,17,16,8,INF,9,3,19],
    [13,19,8,19,12,0,INF,13,4],
    [3,3,7,6,9,15,16,INF,15],
    [5,13,15,19,6,5,5,2,INF],
]

test('7', costs)

# вариант 8
costs = [
    [INF,1,14,18,11,5,13,18,17,5,11],
    [4,INF,19,14,5,3,6,15,14,15,14],
    [12,6,INF,16,19,15,6,2,12,15,8],
    [14,4,18,INF,15,0,18,13,6,2,8],
    [19,15,19,14,INF,12,9,15,3,11,16],
    [10,6,11,4,15,INF,10,9,0,9,6],
    [16,0,10,17,18,6,INF,4,4,1,0],
    [7,17,17,6,7,12,10,INF,14,9,17],
    [19,5,7,6,16,4,6,17,INF,13,14],
    [2,11,11,16,12,7,14,12,15,INF,0],
    [1,14,10,0,10,3,1,0,5,6,INF],
]

test('8', costs)

# вариант 9
costs = [
    [INF,8,12,7,5,0,11,5,13,9,18,1],
    [10,INF,14,4,7,4,10,10,6,6,4,3],
    [4,16,INF,13,3,2,5,5,15,7,11,19],
    [3,7,11,INF,7,6,14,3,3,8,8,18],
    [11,15,18,12,INF,19,12,13,11,16,1,12],
    [8,7,16,19,1,INF,3,16,12,11,0,5],
    [5,10,8,0,17,10,INF,6,13,1,0,6],
    [6,6,6,5,1,5,17,INF,7,14,11,5],
    [19,8,4,19,13,2,5,14,INF,12,15,16],
    [11,8,8,3,4,3,4,11,2,INF,4,15],
    [9,6,12,0,18,13,14,3,12,16,INF,4],
    [18,10,8,3,18,17,16,19,7,0,12,INF],
]

test('9', costs)

# вариант 10
costs = [
    [INF,10,17,15,0,15,2,16,10,2,6,19,10],
    [1,INF,9,5,13,4,13,9,18,10,14,2,9],
    [7,9,INF,12,13,12,7,7,9,15,0,3,12],
    [6,1,19,INF,9,17,4,1,0,10,10,15,18],
    [13,9,9,8,INF,2,6,4,14,2,0,17,9],
    [17,10,10,13,1,INF,14,8,14,17,14,14,2],
    [17,18,3,2,6,0,INF,19,14,3,13,3,13],
    [0,4,1,9,6,6,16,INF,3,19,8,15,4],
    [15,7,5,14,6,10,1,4,INF,4,16,17,19],
    [1,9,18,7,16,16,1,19,16,INF,1,6,12],
    [7,6,7,13,8,18,10,5,19,9,INF,5,10],
    [10,16,10,5,2,5,9,13,6,7,9,INF,7],
    [18,19,4,14,13,12,7,11,8,11,12,13,INF],
]

test('10', costs)

f.close()