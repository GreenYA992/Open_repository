from random import randint as rand
import time
# Задание 2
# Сложность алгоритма O(log n) — временная сложность бинарного поиска,
# где n — количество элементов в массиве. Это означает, что время выполнения увеличивается
# логарифмически с увеличением размера вводных дынных.
# Задание 3 и 4
# Если брать список из 100 чисел, время выполнения будет примерно одинаковое,
# Линейная функция * 100: 0.0097 и Бинарная функция * 100: 0.0094,
# при параметрах 1000000 чисел от 1 до 10000, результат бинарной функции 1.2 сек, линейной 122 сек.
# Но так же многое зависит от того, под каким элементом находится искомое число.

target = int(input('Введите число, которое нужно найти: '))

def digits_gen():
    arr = []
    for i in range(100):
        arr.append(rand(1,100))
    arr.sort()
    #print(arr)
    return arr

def binary_search():
    arr = digits_gen()
    first = 0
    mid = len(arr) // 2
    last = len(arr) - 1
    while arr[mid] != target and first <= last:
        if target > arr[mid]:
            first = mid + 1
        else:
            last = mid - 1
        mid = (first + last) // 2
    if first > last:
        return -1
    else:
        return f'Число {target} найдено, номер элемента {mid}'
start_time = time.time()
print(binary_search())
end_time = time.time()
execution_time = (end_time - start_time) * 100
print(f'Время выполнения функции: {execution_time} секунд')

def linear_search():
    arr = digits_gen()
    for i in range(len(arr)):
        if arr[i] == target:
            return f'Число {target} найдено, номер элемента {i}'
    return -1
start_time = time.time()
print(linear_search())
end_time = time.time()
execution_time = (end_time - start_time) * 10000
print(f'Время выполнения функции: {execution_time} секунд')

start_time = time.time()
for _ in range(100): linear_search()
end_time = time.time()
execution_time = (end_time - start_time)
print(f'Линейная функция * 100: {execution_time} секунд')

start_time = time.time()
for _ in range(100): binary_search()
end_time = time.time()
execution_time = (end_time - start_time)
print(f'Бинарная функция * 100: {execution_time} секунд')
