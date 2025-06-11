# Задача 1 и 2
class HashTable:
    def __init__(self, size):
        self.size = size
        self.table = [[] for _ in range(size)] # Создаем пустые списки, столько раз, каков размер нашей таблицы
    def hash_function(self, key):
        return hash(key) % self.size
    def insert(self, key, value):
        index = self.hash_function(key)
        box = self.table[index]
        for i, pair in enumerate(box):
            if pair[0] == key:
                box[i] = (key, value)
                return
        box.append([key, value])
    def get(self, key):
        index = self.hash_function(key)
        box = self.table[index]
        for pair in box:
            if pair[0] == key:
                return pair[1]
        return None
    def delete(self, key):
        index = self.hash_function(key)
        box = self.table[index]
        for i, pair in enumerate(box):
            if pair[0] == key:
                del box[i]
                return True
        return False
    def search(self, key):
        index = self.hash_function(key)
        box = self.table[index]
        for pair in box:
            if pair[0] == key:
                return pair
        return None
    def resize(self):
        old_table = self.table[:]
        new_size = self.size * 2
        self.size = new_size
        self.table = [[] for _ in range(new_size)]  # Создаем новую таблицу удвоенного размера
        for box in old_table:
            for key, value in box:
                self.insert(key, value)

table = HashTable(10)
table.insert('Томас', 5)
table.insert('apple', 10)
print(table.search('apple'))
table.resize()
print(table.search('apple'))
print(table.get('apple'))
table.delete('apple')
print(table.get('apple'))
print('==========')

# Задача 3
def simple_hash(s):
    return sum(ord(c) for c in s)
# Задача 4
def add_element(hash_dict, string):
    hashed_value = simple_hash(string)
    hash_dict[string] = hashed_value
def find_by_key(hash_dict, key):
    return hash_dict.get(key, None)
hash_dictionary = {}  # словарь
add_element(hash_dictionary, 'hello')
add_element(hash_dictionary, 'world')
add_element(hash_dictionary, 'python')
print(find_by_key(hash_dictionary, 'hello'))  # Выведет хеш 'hello'
print(find_by_key(hash_dictionary, 'world'))  # Выведет хеш 'world'
print(find_by_key(hash_dictionary, 'nonexistent'))  # Выведет None
