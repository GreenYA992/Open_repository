from collections import deque

# Задача 1, 2 и 3
class Node:
    def __init__(self, key):
        self.left = None
        self.right = None
        self.val = key

class BinaryTree:
    def __init__(self):
        self.root = None
    def insert(self, key):
        if self.root is None:
            self.root = Node(key)
        else:
            self._insert_recursive(self.root, key)
    def _insert_recursive(self, current_node, key):
        if key < current_node.val:
            if current_node.left is None:
                current_node.left = Node(key)
            else:
                self._insert_recursive(current_node.left, key)
        elif key >= current_node.val:
            if current_node.right is None:
                current_node.right = Node(key)
            else:
                self._insert_recursive(current_node.right, key)
    def search(self, key):
        return self._search_recursive(self.root, key)
    def _search_recursive(self, current_node, key):
        if current_node is None or current_node.val == key:
            return current_node is not None
        if key < current_node.val:
            return self._search_recursive(current_node.left, key)
        return self._search_recursive(current_node.right, key)
    def bfs_traversal(self):
        if self.root is None:
            return []
        result = []
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            result.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        return result

    def preorder_traversal(self):
        return self._preorder_recursive(self.root)

    def _preorder_recursive(self, node):
        if node is None:
            return []
        return [node.val] + self._preorder_recursive(node.left) + self._preorder_recursive(node.right)

    def inorder_traversal(self):
        return self._inorder_recursive(self.root)

    def _inorder_recursive(self, node):
        if node is None:
            return []
        return self._inorder_recursive(node.left) + [node.val] + self._inorder_recursive(node.right)

    def postorder_traversal(self):
        return self._postorder_recursive(self.root)

    def _postorder_recursive(self, node):
        if node is None:
            return []
        return self._postorder_recursive(node.left) + self._postorder_recursive(node.right) + [node.val]

# Задача 4
class AVLNode(Node):
    def __init__(self, val):
        super().__init__(val)
        self.height = 1


class AVLTree(BinaryTree):
    def insert(self, val):
        self.root = self._insert_avl(self.root, val)
    def _insert_avl(self, node, val):
        if node is None:
            return AVLNode(val)
        elif val < node.val:
            node.left = self._insert_avl(node.left, val)
        else:
            node.right = self._insert_avl(node.right, val)
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
        balance_factor = self.get_balance(node)
        if balance_factor > 1 and val < node.left.val:
            return self.right_rotate(node)
        if balance_factor < -1 and val > node.right.val:
            return self.left_rotate(node)
        if balance_factor > 1 and val > node.left.val:
            node.left = self.left_rotate(node.left)
            return self.right_rotate(node)
        if balance_factor < -1 and val < node.right.val:
            node.right = self.right_rotate(node.right)
            return self.left_rotate(node)
        return node
    def get_height(self, node):
        if node is None:
            return 0
        return node.height
    def get_balance(self, node):
        if node is None:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)
    def left_rotate(self, z):
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        return y
    def right_rotate(self, y):
        x = y.left
        T3 = x.right
        x.right = y
        y.left = T3
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))
        return x

avltree = AVLTree()
avltree.insert(10)
avltree.insert(20)
avltree.insert(30)
avltree.insert(40)
avltree.insert(50)
avltree.insert(25)

print(avltree.bfs_traversal())
print(avltree.preorder_traversal())
print(avltree.inorder_traversal())
print(avltree.postorder_traversal())
