# Задание 1, 2, 3 и 4
from collections import deque

class DirectedGraph:
    def __init__(self):
        self.graph_list = {} # Представление графа в виде словаря смежности
    def __str__(self):
        return str(self.graph_list)
    def add_vertex(self, vertex):
        if vertex not in self.graph_list:
            self.graph_list[vertex] = []
    def add_edge(self, source, destination):
        if source not in self.graph_list:
            self.add_vertex(source)
        if destination not in self.graph_list:
            self.add_vertex(destination)
        self.graph_list[source].append(destination)

    def breadth_first_search(self, start_vertex):
        queue = deque([start_vertex])
        visited = set(start_vertex)
        traversal = []
        while queue:
            vertex = queue.popleft()
            traversal.append(vertex)
            for neighbor in self.graph_list.get(vertex, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return traversal

    def create_matrix(self):
        vert = sorted(list(self.graph_list.keys()))
        num_vert = len(vert)
        matrix = [[0] * num_vert for _ in range(num_vert)]
        vertex_to_index = {vert: idx for idx, vert in enumerate(vert)}
        for source, destinations in self.graph_list.items():
            s_idx = vertex_to_index[source]
            for dest in destinations:
                d_idx = vertex_to_index[dest]
                matrix[s_idx][d_idx] = 1
        return matrix

    def new_list(self):
        print('\nСписок смежности')
        for key, value in self.graph_list.items():
            print(key, ':', value)

# Создание DirectedGraph
gr = DirectedGraph()
gr.add_vertex('A')
gr.add_vertex('B')
gr.add_vertex('C')
gr.add_edge('A', 'B')
gr.add_edge('B', 'C')
gr.add_edge('C', 'A')

print('\nОриентированный граф:')
print(gr)

# Создание матрицы смежности
mat = gr.create_matrix()
print('\nМатрица смежности:')
for row in mat:
    print(row)

# Выполнение обхода в ширину
bfs_traversal = gr.breadth_first_search('A')
print('\nОбход в ширину (начиная с вершины "A"): ', bfs_traversal)

# Создание списка смежности
gr.new_list()
