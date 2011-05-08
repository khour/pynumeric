#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import copy

class HungarianAlgorithm:

    def __init__(self):
        self.C = None
        self.row_covered = []
        self.col_covered = []
        self.n = 0
        self.Z0 = (0, 0)
        self.marked = None
        self.path = None

    def solve(self, cost_matrix):
        """
        Вычисляет индексы пар строка-столбец с наименьшей общей
        стоимостью. Возвращает список пар (строка, столбец).
        """
        self.C = copy.deepcopy(cost_matrix)
        self.n = len(self.C)
        self.__clear_covers()
        self.Z0 = (0, 0)
        self.path = self.__make_matrix(self.n * 2, 0)
        self.marked = self.__make_matrix(self.n, 0)

        steps = { 1 : self.__step1,
                  2 : self.__step2,
                  3 : self.__step3,
                  4 : self.__step4,
                  5 : self.__step5,
                  6 : self.__step6 }
        
        iteration_count = 1
        step = 1
        while step < 7:
            if step == 3:
                iteration_count += 1
            func = steps[step]
            step = func()

        # просмотреть помеченные ячейки
        results = [(i, j) for i, row in enumerate(self.marked) \
                          for j, el in enumerate(row) if el == 1]

        return results, iteration_count

    def __make_matrix(self, n, val):
        """Создать n x n матрицу, заполненную val."""
        return [[val for j in xrange(n)] for i in xrange(n)]

    def __step1(self):
        """
        Найти минимальный элемент в каждой строке, вычесть его из строки.
        Перейти к шагу 2.
        """
        self.C = [[el - min(row) for el in row] for row in self.C]
        return 2

    def __step2(self):
        """
        Найти нуль (Z) в результирующей матрице. Если в строке и столбце
        этого элемента нет единиц, то пометить Z. Повторить для каждого
        элемента матрицы. Перейти к шагу 3.
        """
        for i, row in enumerate(self.C):
            for j, el in enumerate(row):
                if (el == 0 and not self.row_covered[i] and
                                not self.col_covered[j]):
                    self.marked[i][j] = 1
                    self.col_covered[j] = True
                    self.row_covered[i] = True

        self.__clear_covers()
        return 3

    def __step3(self):
        """
        Покрыть каждый столбец, содержащий единицу. Если >= n
        столбцов помечено, то единицы в результирующей матрице
        описывают полный набор уникальных назначений. В этом
        случае перейти к DONE, иначе - к шагу 4.
        """
        count = 0
        for i, row in enumerate(self.marked):
            for j, (el, c_cov) in enumerate(zip(row, self.col_covered)):
                if el == 1:
                    self.col_covered[j] = True
                    count += 1

        if count >= self.n:
            return 7 # done
        else:
            return 4

    def __step4(self):
        """
        Найти в матрице непокрытый нуль и сделать главным (2). Если в строке,
        содержащей этот нуль, нет помеченных (1) элементов, то перейти к шагу 5.
        Иначе, покрыть строку и снять покрытие с колонки, содержащих
        помеченный (1) нуль. Продолжать до тех пор, пока есть непокрытые
        нули. Сохранить наименьшее непокрытое значение и перейти к шагу 6.
        """
        while True:
            row, col = self.__find_a_zero()
            if row >= 0:
                self.marked[row][col] = 2
                star_col = self.__find_star_in_row(row)
                if star_col >= 0:
                    self.row_covered[row] = True
                    self.col_covered[star_col] = False
                else:
                    self.Z0 = (row, col)
                    return 5
            else:
                return 6

    def __step5(self):
        """
        Сформировать цепь чередующихся главных и помеченных нулей.
        Пусть Z0 представляет собой непокрытый нуль, найденный на шаге 4.
        Z1 - первый помеченный нуль в столбце Z0. Z2 - главный нуль в
        строке Z1. Строить до тех пор, пока не появится главный нуль, в
        столбце которого нет помеченных нолей.
        Снять метку со всех помеченных нулей в цепи, пометить главные.
        Обнулить все главные нули, сбросить покрытие. Перейти на шаг 3.
        """
        path = self.path
        path[0] = self.Z0
        count = 0
        while True:
            row = self.__find_star_in_col(path[count][1])
            if row >= 0:
                count += 1
                path[count] = (row, path[count - 1][1])

                col = self.__find_prime_in_row(path[count][0])
                if col >= 0:
                    count += 1
                    path[count] = (path[count - 1][0], col)
            else:
                break

        self.__convert_path(path, count)
        self.__clear_covers()
        self.__erase_primes()
        return 3

    def __step6(self):
        """
        Добавить значение, найденное на шаге 4, к каждому элементу
        каждой покрытой строки. Вычесть его из каждого элемента
        каждого непокрытого столбца. Перейти к шагу 4.
        """
        minval = self.__find_smallest()

        self.C = [[el + minval if (r_cov and c_cov) else \
                   el - minval if (not r_cov and not c_cov) else el \
                   for el, c_cov in zip(row, self.col_covered)] \
                   for row, r_cov in zip(self.C, self.row_covered)]

        return 4

    def __find_smallest(self):
        """Найти наименьшее непокрытое значение в матрице."""
        minval = sys.maxint
        for row, r_col in zip(self.C, self.row_covered):
            for el, c_col in zip(row, self.col_covered):
                if not r_col and not c_col and el < minval:
                    minval = el
        return minval

    def __find_a_zero(self):
        """Найти первый непокрытый элемент со значением 0."""
        for i, (row, r_cov) in enumerate(zip(self.C, self.row_covered)):
            for j, (el, c_cov) in enumerate(zip(row, self.col_covered)):
                if el == 0 and not r_cov and not c_cov:
                    return i, j

        return -1, -1

    def __find_star_in_row(self, row):
        """
        Найти первый помеченный (1) элемент в строке. Возвращает индекс
        столбца, или -1, если такого элемента нет.
        """
        try:
            return self.marked[row].index(1)
        except ValueError:
            return -1

    def __find_star_in_col(self, col):
        """
        Найти первый помеченный (1) элемент в столбце. Возвращает индекс
        строки, или -1, если такого элемента нет.
        """
        try:
            return zip(*self.marked)[col].index(1)
        except ValueError:
            return -1

    def __find_prime_in_row(self, row):
        """
        Найти первый главный (2) элемент в строке. Возвращает индекс
        столбца, или -1, если таких элементов нет.
        """
        try:
            return self.marked[row].index(2)
        except ValueError:
            return -1

    def __convert_path(self, path, count):
        for i, path_el in zip(xrange(count + 1), path):
            row, col = path_el[0], path_el[1]
            value = self.marked[row][col]
            self.marked[row][col] = 0 if value == 1 else 1

    def __clear_covers(self):
        """Очистить все покрытые строки и столбцы"""
        self.row_covered = [False for i in xrange(self.n)]
        self.col_covered = [False for i in xrange(self.n)]

    def __erase_primes(self):
        """Очистить все главные метки"""
        convert = lambda el: 0 if el == 2 else el
        self.marked = [[convert(el) for el in row] for row in self.marked]

def print_matrix(matrix):
    """Вывести на экран матрицу"""
    import math

    width = 0
    for row in matrix:
        for val in row:
            if val < 0: val = -10 * val
            if val == 0: val = 1
            width = max(width, int(math.log10(val)) + 1)

    format = '%%%dd' % width

    # Print the matrix
    for row in matrix:
        sep = '['
        for val in row:
            sys.stdout.write(sep + format % val)
            sep = ', '
        sys.stdout.write(']\n')


# main
if __name__ == '__main__':

    import sys
    stdout = sys.stdout

    f = open('HungarianAlgorithm.txt', 'w+')

    def test(msg, cost_matrix):
        sys.stdout = f
        print '\n', msg,
        sys.stdout = stdout
        indexes, iteration_count = HungarianAlgorithm().solve(cost_matrix)
        sys.stdout = f
        print ':', iteration_count, 'iterations'
        for index in indexes:
            print index[0] + 1, '\t',
        print
        for index in indexes:
            print index[1] + 1, '\t',
        print
        print 'Total cost:', sum(cost_matrix[i][j] for i, j in indexes)
        sys.stdout = stdout
        
    
    # вариант 1
    cost_matrix = [
        [6,     4,  13, 4,  19, 15, 11, 8],
        [17,    15, 18, 14, 0,  7,  18, 7],
        [3,     5,  11, 9,  7,  7,  18, 16],
        [17,    10, 16, 19, 9,  6,  1,  5],
        [14,    2,  10, 13, 11, 6,  4,  10],
        [17,    11, 17, 12, 1,  10, 6,  19],
        [13,    1,  4,  2,  2,  7,  2,  14],
        [12,    15, 19, 11, 13, 1,  7,  8],
    ]

    test('1', cost_matrix)
    
    # вариант 2
    cost_matrix = [
        [9,6,4,9,3,8,0],
        [5,8,6,8,8,3,5],
        [5,2,1,1,8,6,8],
        [1,0,9,2,5,9,2],
        [9,2,3,3,0,3,0],
        [7,3,0,9,4,5,6],
        [0,9,6,0,8,8,9],
    ]
    
    test('2', cost_matrix)
    
    # вариант 3
    cost_matrix = [
        [6,6,2,4,7,1,9,4,6],
        [5,0,2,4,9,2,9,2,0],
        [7,6,0,5,2,3,0,5,5],
        [9,5,8,9,2,3,1,5,7],
        [3,1,7,3,0,2,2,8,1],
        [3,0,0,6,1,7,2,4,7],
        [5,6,1,9,9,8,4,1,8],
        [5,4,5,2,2,6,6,5,6],
        [3,6,1,6,3,0,5,2,2],
    ]
    
    test('3', cost_matrix)
    
    # вариант 4
    cost_matrix = [
        [6,5,6,8,4,0,4,6],
        [5,7,8,7,4,4,0,9],
        [0,7,9,2,8,7,0,3],
        [6,6,6,3,0,3,0,8],
        [7,4,7,1,1,1,8,9],
        [8,0,7,5,0,9,1,3],
        [3,2,4,7,1,7,3,4],
        [9,2,4,3,2,4,3,9],
    ]
    
    test('4', cost_matrix)
    
    # вариант 5
    cost_matrix = [
        [7,4,5,3,8,9,6,5,5,3,2],
        [5,6,9,4,9,0,0,4,4,7,2],
        [8,8,3,2,7,3,7,6,7,4,6],
        [7,4,9,9,3,7,3,8,1,5,8],
        [5,2,4,3,3,9,6,2,5,1,3],
        [9,4,5,8,6,3,3,1,7,6,5],
        [9,1,0,3,1,2,7,6,9,4,6],
        [5,6,8,0,9,9,1,9,3,0,8],
        [4,6,5,6,4,7,5,3,8,0,1],
        [2,3,7,8,4,9,5,0,2,8,0],
        [7,6,7,1,9,5,7,4,2,3,0],
    ]
    
    test('5', cost_matrix)
    
    # вариант 6
    cost_matrix = [
        [7,-4,5,3,8,9,6,5],
        [5,6,9,4,9,0,0,4],
        [8,8,3,-2,7,-3,7,6],
        [7,4,9,9,3,7,3,8],
        [5,2,4,3,3,9,6,2],
        [9,4,5,8,6,3,3,1],
        [9,1,0,-3,1,2,7,6],
        [5,6,8,0,9,9,1,9],
    ]
    
    test('6', cost_matrix)
    
    # вариант 7
    cost_matrix = [
        [2,6,5,-1,6,1,8,4,6],
        [2,1,2,7,9,-2,8,2,0],
        [0,6,0,5,1,3,4,3,5],
        [7,0,8,9,2,4,1,6,7],
        [-1,1,0,-3,0,2,2,2,1],
        [3,0,6,6,1,-2,2,4,0],
        [1,7,1,9,4,8,2,6,8],
        [5,1,5,2,2,6,-1,5,4],
        [3,6,0,6,3,0,9,1,2],
    ]
    
    test('7', cost_matrix)
    
    # вариант 8
    cost_matrix = [
        [2,4,0,3,8,-1,6,5],
        [8,6,3,4,2,0,0,4],
        [8,-4,3,2,7,3,1,0],
        [2,4,9,5,3,0,3,8],
        [5,2,7,3,-1,0,3,2],
        [3,2,5,1,5,3,0,1],
        [2,1,0,-3,1,2,7,0],
        [1,6,4,0,0,9,1,7],
    ]
    
    test('8', cost_matrix)

    f.close()