# Задача 1 и 2
import heapq
import time
from random import randint as rand

class Task:
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration
    def __repr__(self):
        return f'Task({self.name}, duration={self.duration})'
class PriorityQueue:
    def __init__(self):
        self.heap = []
    def is_empty(self):
        return len(self.heap) == 0
    def enqueue(self, task, priority):
        heapq.heappush(self.heap, (priority, task))
    def dequeue(self):
        if not self.is_empty():
            return heapq.heappop(self.heap)[1]
        return None
    def peek(self):
        if not self.is_empty():
            return self.heap[0][1]
        return None
    def size(self):
        return len(self.heap)

pqueue = PriorityQueue()
pqueue.enqueue(10, 3)
pqueue.enqueue(152, 1)
pqueue.enqueue('Томас', 2)
pqueue.enqueue(True, 4)
print(pqueue.is_empty())
print(pqueue.peek())
print(pqueue.size())
pqueue.dequeue()
print(pqueue.peek())
print(pqueue.size())

# Задача 3 и 4
# На примере списка из 10 чисел, пузырьковая сортировка сработала быстрее всего
# (время * 10000: merge_iter - 0.66 сек, merge - 0.54 сек и bubble - 0.43 сек.).
# На примере списка из 100 чисел, лучше сработала merge_iter и merge,
# (время * 10000: merge_iter - 3.87 сек, merge - 3.81 сек и bubble - 13.15 сек.).
# На примере списка из 1000 чисел, лучше сработала merge_iter и merge,
# (время * 10000: merge_iter - 69.58 сек, merge - 70.21 сек и bubble - 890.27 сек.).
def digits_gen():
    lst = []
    for i in range(1000):
        lst.append(rand(1,1000))
    return lst

def merge_new(left, right):
    res = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            res.append(left[i])
            i += 1
        else:
            res.append(right[j])
            j += 1
    res.extend(left[i:])
    res.extend(right[j:])
    return res
def merge_sort_iter(lst):
    width = 1
    n = len(lst)
    while width < n:
        for i in range(0, n, 2 * width):
            left = lst[i:i + width]
            right = lst[i + width:i + 2 * width]
            lst[i:i + 2 * width] = merge_new(left, right)
        width *= 2
    return lst
print(f'Неотсортированный список: {digits_gen()}')
start_time = time.time()
print(f'Update слияние: {merge_sort_iter(digits_gen())}')
end_time = time.time()
execution_time = (end_time - start_time) * 10000
print(f'Улучшенная сортировка слиянием * 10000: {round(execution_time, 2)} секунд')
print('==================================')
print('==================================')

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

def bubble_sort(lst):
    n = len(lst)
    for i in range(n):
        for j in range(0, n-i-1):
            if lst[j] > lst[j+1]:
                lst[j], lst[j+1] = lst[j+1], lst[j]
    return lst
print(f'Неотсортированный список: {digits_gen()}')
start_time = time.time()
print(f'Пузырьковая сортировка: {bubble_sort(digits_gen())}')
end_time = time.time()
execution_time = (end_time - start_time) * 10000
print(f'Пузырьковая сортировка * 10000: {round(execution_time, 2)} секунд')
print('==================================')
