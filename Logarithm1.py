# Задача 1 и 2
#Временная сложность O(n), так как время выполнения зависит от количества элементов в списке. Чем больше элементов, тем больше времени
#Пространственная O(1), так как для его выполнения требуется постоянное кол-во дополнительного пространства, независимо от входных данных
import timeit
def linear_search_1(lst, key):
    for i in range(len(lst)):
        if lst[i] == key:
            return i
    return -1
lst = [2, 4, 7, 5, 8, 10]
key = 5
s = """def linear_search_test():
    lst = [2, 4, 7, 5, 8, 10]
    key = 5
    def linear_search_1(lst, key):
        for i in range(len(lst)):
            if lst[i] == key:
                return i
        return -1
"""
print(timeit.timeit(stmt=s, number=100))
print(linear_search_1(lst, key))

def linear_search(lst, key):
    for i in range(len(lst)):
        if lst[i] == key:
            return i
    return -1
lst = list(map(int, input('Введите список из числе, через ", " : ').split(', ')))
s = """def linear_search_test():
    lst = [2, 4, 7, 5, 8, 10]
    key = 5
    def linear_search(lst, key):
        for i in range(len(lst)):
            if lst[i] == key:
                return i
        return -1
"""
print(linear_search(lst, int(input('Введите число, номер элемента которого мы ищем : '))))
print(timeit.timeit(stmt=s, number=100))

# Задача 3 и 4 Чем короче список, тем быстрее ма находим числа таким методом
# Список из 10 чисел обработался за 0.002 сек, из 10000 за 0.93 сек. В обоих примерах числа в списке не было
from random import randint
import time
start_time = time.time()
def linear_search_2(lst_1, key_1):
    for j in range(len(lst_1)):
        if lst_1[j] == key_1:
            return j
    return -1
lst_1 = [randint(1, 100) for i in range(10)]
end_time = time.time()
execution_time = (end_time - start_time) * 100
print(lst_1)
print(linear_search_2(lst_1, int(input())))
print(f'Время выполнения функции: {execution_time} секунд')
