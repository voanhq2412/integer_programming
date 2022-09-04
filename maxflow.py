import numpy as np
import heapq as hq
import copy

# array = np.array(
#     [
#         [0, 5, 10, 15, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 20, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 25, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 25, 0, 10, 0, 0, 0],
#         [0, 0, 0, 5, 0, 0, 0, 0, 30, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 20, 10, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 15],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     ]
# )


# array = np.array(
#     [
#         [0, 99, 99, 99, 0, 0, 0],
#         [0, 0, 15 / 2, 15 / 2, 0, 0, 0],
#         [0, 0, 0, 20 / 3, 20 / 3, 20 / 3, 0],
#         [0, 0, 4 / 3, 0, 4 / 3, 4 / 3, 0],
#         [0, 0, 0, 0, 0, 0, 1 / 6],
#         [0, 0, 0, 0, 0, 0, 5],
#         [0, 0, 0, 0, 0, 0, 0],
#     ]
# )


# # # # PPt slide example
# array = np.array(
#     [
#         [0, 8, 8, 0, 0, 0],
#         [0, 0, 2, 6, 0, 0],
#         [0, 1, 0, 3, 0, 0],
#         [0, 0, 0, 0, 10, 0],
#         [0, 0, 0, 0, 0, 8],
#         [0, 0, 0, 0, 0, 0],
#     ]
# )


class dinic:
    def __init__(self, array):
        self.array = array
        self.n = len(array)
        self.visited = self.path = np.zeros(self.n)
        self.bottleneck_nodes = np.zeros(self.n)

    def max_flow(self):
        self.total_bottleneck = 0
        while True:
            array = copy.deepcopy(self.array)
            level_graph = self.bfs(self.array)
            print(level_graph)
            if np.array_equal(level_graph, array):
                break

            self.array = copy.deepcopy(level_graph)
            self.dfs(0, 999999)
            self.get_bottlenecks(level_graph, self.array)
        return self.total_bottleneck, self.bottleneck_nodes

    def get_bottlenecks(self, level_graph, remaining_capacity):
        lg = np.ceil(level_graph)
        rc = np.ceil(remaining_capacity)
        lg[lg > 0] = 1
        rc[rc > 0] = 1
        diff = lg.sum(axis=1) - rc.sum(axis=1)

        self.bottleneck_nodes += diff
        self.bottleneck_nodes[self.bottleneck_nodes > 0] = 1

    # Obtain level graph with Breath-First-Search
    def bfs(self, array):
        self.visited.fill(0)
        self.visited[0] = 1
        q = []
        hq.heappush(q, (0))
        while sum(self.visited) != self.n:
            out = []
            while len(q) > 0:
                s = hq.heappop(q)
                out += list(np.where(np.multiply(array[s], 1 - self.visited) > 0)[0])
                array[s, [i for i in range(self.n) if i not in out]] = 0

            for i in out:
                self.visited[i] = 1
                hq.heappush(q, (i))

            if len(q) == 0:
                break
        return array

    # Look for augmenting paths with Depth-First-Search
    # can only traverse edges with positive capacity
    def dfs(self, s, bottleneck):
        out = list(np.where(self.array[s] > 0)[0])
        if s == (self.n - 1):
            self.total_bottleneck += bottleneck
            self.readjust_capacity(bottleneck)

        for i in out:
            self.path[s] = i
            self.dfs(i, min(bottleneck, self.array[s, i]))

    # Subtract bottleneck value from all edges of the augmenting path
    def readjust_capacity(self, bottleneck):
        s = 0
        while True:
            self.array[s, int(self.path[s])] -= bottleneck
            s = int(self.path[s])
            if s == (self.n - 1):
                break


# max_flow = dinic(array).bfs(array)
# print(max_flow)


# array = np.array(
#     [
#         [0, 0, 0, 0, 0, 1.702127659574468, 0, 1.702127659574468, 99, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 99, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 99, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 99, 0, 0],
#         [0, 0, 0, 2.8125, 0, 0, 0, 2.8125, 99, 0, 0],
#         [
#             3.4285714285714284,
#             3.4285714285714284,
#             0,
#             0,
#             0,
#             0,
#             0,
#             3.4285714285714284,
#             99,
#             0,
#             0,
#         ],
#         [
#             0,
#             0,
#             0,
#             1.2804878048780488,
#             1.2804878048780488,
#             1.2804878048780488,
#             0,
#             0,
#             99,
#             0,
#             1.2804878048780488,
#         ],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [99, 99, 0, 99, 99, 99, 99, 99, 99, 99, 99],
#         [0, 0, 0, 0, 0, 0, 0, 0, 99, 0, 0],
#     ]
# )

# max_flow = dinic(array).max_flow()
# print(max_flow)
