# Задача 1
# При условии, что предмет можно взять много раз
def new_knapsack(max_w, wt, val, n):
    dp = [0] * (max_w + 1)
    for i in range(n):
        for w in range(wt[i], max_w + 1):
            dp[w] = max(dp[w], val[i] + dp[w - wt[i]])
    return dp[max_w]

val = [10, 500, 150]
wt = [50, 500, 30]
max_w = 580
n = len(val)
print(new_knapsack(max_w, wt, val, n))

# При условии, что предмет можно взять только 1 раз
def knapsack_new(max_w, wt, val, n):
    dp = [[0 for _ in range(max_w + 1)] for _ in range(n + 1)]
    for i in range(n + 1):
        for w in range(max_w + 1):
            if i == 0 or w == 0:
                dp[i][w] = 0
            elif wt[i - 1] <= w:
                dp[i][w] = max(val[i - 1] + dp[i - 1][w - wt[i - 1]], dp[i - 1][w])
            else:
                dp[i][w] = dp[i - 1][w]
    return dp[n][max_w]

val = [10, 500, 150]
wt = [50, 500, 30]
max_w = 580
n = len(val)
print(knapsack_new(max_w, wt, val, n))

# Задача 2
def lcs_length(s1, s2):
    m = len(s1)
    n = len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]

s1 = "ABCDGH"
s2 = "AEDFHR"
print(lcs_length(s1, s2))

# Задача 3
def count_partitions(n):
    ways = [0] * (n + 1)
    ways[0] = 1
    for k in range(1, n + 1):
        for i in range(k, n + 1):
            ways[i] += ways[i - k]
    return ways[n]
print(count_partitions(7))

# Задача 4
def floyd_warshall(graph):
    distance = [row[:] for row in graph]
    n = len(distance)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if distance[i][j] > distance[i][k] + distance[k][j]:
                    distance[i][j] = distance[i][k] + distance[k][j]
    return distance

INF = float('inf')
graph = [
    [0, 5, INF, 10],
    [INF, 0, 3, INF],
    [INF, INF, 0, 1],
    [INF, INF, INF, 0]
]
shortest_paths = floyd_warshall(graph)
for row in shortest_paths:
    print(row)
