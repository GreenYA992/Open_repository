from random import randint as rand
import time

# На примере время выполнения * 10000, сортировка выбором работает немного быстрее,
# 2.36 сек, против 2.72 сек. (в формате * 10000, значения воспринимаются проще)

def selected_sort():
    lst = digits_gen()
    n = len(lst)
    for i in range(n):
        min_index = i
        for j in range(i+1, n):
            if lst[j] < lst[min_index]:
                min_index = j
        lst[i], lst[min_index] = lst[min_index], lst[i]
    return lst

def bubble_sort():
    lst = digits_gen()
    n = len(lst)
    for i in range(n):
        for j in range(0, n-i-1):
            if lst[j] > lst[j+1]:
                lst[j], lst[j+1] = lst[j+1], lst[j]
    return lst

def digits_gen():
    lst = []
    for i in range(50):
        lst.append(rand(1,100))
    print(lst)
    return lst

start_time = time.time()
print(selected_sort())
end_time = time.time()
execution_time = (end_time - start_time) * 10000
print(f'Сортировка выбором * 100: {round(execution_time, 2)} секунд')

start_time = time.time()
print(bubble_sort())
end_time = time.time()
execution_time = (end_time - start_time) * 10000
print(f'Сортировка пузырьком * 100: {round(execution_time, 2)} секунд')
