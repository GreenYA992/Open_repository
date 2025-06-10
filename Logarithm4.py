from random import randint as rand

# Задание 1
def factorial(n):
    if n == 1: # Базовый случай, это условие, при котором рекурсия прекращается
        return 1
    return n * (factorial(n-1))
print(factorial(5))

# Задание 2
def sum_list(lst):
    if len(lst) == 0:
        return 0
    return lst[0] + sum_list(lst[1:])
print(sum_list([1,2,3]))

# Задание 3
def binary_search_func(lst, left, right, target):
    if right > left:
        mid = (left + right) // 2
        if lst[mid] == target:
            return f'Число {target}, номер элемента {mid}'
        elif lst[mid] > target:
            return binary_search_func(lst, left, mid-1, target)
        else:
            return binary_search_func(lst, mid+1, right, target)
    return 'Числа в списке нет' # Можно изменить на -1, но как по мне так аккуратнее и понятнее

lst = []
for i in range(15):
    lst.append(rand(1, 50))
lst.sort()
print(lst)
print(binary_search_func(lst, 0, len(lst), 30))

# Задание 4
class Stack:
    def __init__(self):
        self.stack = []
    def push(self, item): # Добавляет элемент в список
        self.stack.append(item)
    def pop(self): # Удаляет последний элемент из списка
        if not self.is_empty():
            return self.stack.pop()
        return 'Стек пуст'
    def peek(self): # Вызывает последний элемент из списка, без удаления
        if not self.is_empty():
            return self.stack[-1]
        return 'Стек пуст'
    def is_empty(self): # Проверяет пустой ли список
        return len(self.stack) == 0
    def size(self): # Вызывает размер списка
        return len(self.stack)
if __name__ == '__main__':
    stack = Stack()
    stack.push(10)
    stack.push('test')
    stack.push(True)
    print(stack.pop()) # Напечатали элемент из списка, который удалили
    print(stack.peek()) # Напечатали последний элемент из списка, без удаления
    print(stack.is_empty()) # Проверили пустой ли список
    print(stack.size()) # Напечатали размер оставшегося списка
