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
        print '(%d, %d) -> %d' % (row + 1, column + 1, value)
    print 'total cost: %d' % total


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
    indexes = HungarianAlgorithm().solve(problem)
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
        print '\n   Iteration %d,' % itercount,
        print 'problems count = %d' % len(problems)

        res = iteration(problems, min_cost)

        if res is None:
            print 'No suitable solution'
        else:
            min_cost, min_indexes = res
            print 'Found suitable solution:'
            print_indexes(min_indexes, costs)

        itercount += 1

    return min_cost, min_indexes


costs = [
    [INF,   12,     11,     1,      18,     4,      14,     3,      18],
    [9,     INF,    14,     12,     7,      10,     4,      18,     9],
    [7,     8,      INF,    18,     1,      6,      1,      9,      19],
    [10,    18,     0,      INF,    3,      14,     3,      11,     4],
    [7,     3,      17,     10,     INF,    14,     14,     9,      8],
    [17,    16,     17,     16,     8,      INF,    9,      3,      19],
    [13,    19,     8,      19,     12,     0,      INF,    13,     4],
    [3,     3,      7,      6,      9,      15,     16,     INF,    15],
    [5,     13,     15,     19,     6,      5,      5,      2,      INF],
]

min_cost, min_indexes = solve(costs)

print '\nResult solution:'
print_indexes(min_indexes, costs)

