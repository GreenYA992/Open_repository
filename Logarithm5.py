from random import randint as rand
import time

def digits_gen():
    lst = []
    for i in range(10):
        lst.append(rand(1,10))
    return lst

# Задание 1
# Стек вызовов:
# fibonacci(5)
# ├── fibonacci(4)
# │   ├── fibonacci(3)
# │   │   ├── fibonacci(2)
# │   │   │   ├── fibonacci(1) ⇒ 1
# │   │   │   └── fibonacci(0) ⇒ 0
# │   │   └── fibonacci(1) ⇒ 1
# │   └── fibonacci(2)
# │       ├── fibonacci(1) ⇒ 1
# │       └── fibonacci(0) ⇒ 0
# └── fibonacci(3)
#     ├── fibonacci(2)
#     │   ├── fibonacci(1) ⇒ 1
#     │   └── fibonacci(0) ⇒ 0
#     └── fibonacci(1) ⇒ 1
def fibonacci(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    return fibonacci(n-1) + fibonacci(n-2)
print(fibonacci(5))

# Задание 2
def merge_sort(lst):
    if len(lst) > 1:
        mid = len(lst) // 2
        left_half = lst[:mid]
        right_half = lst[mid:]
        merge_sort(left_half)
        merge_sort(right_half)
        i = j = k = 0
        while i < len(left_half) and j < len(right_half):
            if left_half[i] < right_half[j]:
                lst[k] = left_half[i]
                i += 1
            else:
                lst[k] = right_half[j]
                j += 1
            k += 1
        while i < len(left_half):
            lst[k] = left_half[i]
            i += 1
        while j < len(right_half):
            lst[k] = right_half[j]
            j += 1
            k += 1
    return lst
print(f'Неотсортированный список: {digits_gen()}')
start_time = time.time()
print(f'Сортировка слиянием: {merge_sort(digits_gen())}')
end_time = time.time()
execution_time = (end_time - start_time) * 10000
print(f'Сортировка слиянием * 10000: {round(execution_time, 2)} секунд')
print('==================================')

# Задание 3
def quick_sort(lst):
    if len(lst) <= 1:
        return lst
    else:
        pivot = lst[len(lst) // 2]
        left_lst = []
        middle = []
        right_lst = []
        for i in lst:
            if i > pivot:
                right_lst.append(i)
            elif i < pivot:
                left_lst.append(i)
            else:
                middle.append(i)
        return quick_sort(left_lst) + middle + quick_sort(right_lst)
print(f'Неотсортированный список: {digits_gen()}')
start_time = time.time()
print(f'Быстрая сортировка: {quick_sort(digits_gen())}')
end_time = time.time()
execution_time = (end_time - start_time) * 10000
print(f'Быстрая сортировка * 10000: {round(execution_time, 2)} секунд')
print('==================================')

# Задание 4
# На примере списка из 10 чисел, 'Сортировка вставками' работает быстрее (*10000 - 0.41 сек, против 0.52 сек)
# На примере списка из 100 чисел, 'Быстрая сортировка' работает быстрее (*10000 - 3.59 сек, против 5.75 сек)
# На примере списка из 1000 чисел, 'Быстрая сортировка' работает быстрее (*10000 - 69.38 сек, против 399.69 сек)
def insertion_sort(lst):
    for i in range(len(lst)):
        j = i - 1
        k = lst[i]
        while lst[j] > k and j >= 0:
            lst[j + 1] = lst[j]
            j -= 1
        lst[j + 1] = k
    return lst
print(f'Неотсортированный список: {digits_gen()}')
start_time = time.time()
print(f'Быстрая сортировка: {insertion_sort(digits_gen())}')
end_time = time.time()
execution_time = (end_time - start_time) * 10000
print(f'Сортировка вставками * 10000: {round(execution_time, 2)} секунд')
