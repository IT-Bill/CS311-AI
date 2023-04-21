import numpy as np
from heapq import heappop, heappush

MAX_COST = int(1e9)

def read_file(path):
    with open(path, "r") as f:
        contents = f.readlines()
    num_vertices = int(contents[1].split(":")[1])
    depot = int(contents[2].split(":")[1]) - 1  # ! 减一
    num_required_edges = int(contents[3].split(":")[1])
    num_non_required_edges = int(contents[4].split(":")[1])
    num_vehicles = int(contents[5].split(":")[1])
    capacity = int(contents[6].split(":")[1])
    total_cost = int(contents[7].split(":")[1])

    graph = np.zeros((num_vertices, num_vertices), dtype=int)
    graph.fill(MAX_COST)
    tasks = []

    for c in contents[9: 9 + num_required_edges + num_non_required_edges]:
        c = [int(i) for i in c.split()]
        n1, n2 = c[0] - 1, c[1] - 1
        graph[n1, n2] = c[2]
        graph[n2, n1] = c[2]
        if c[3] != 0:
            tasks.append(((n1, n2), c[3]))


    info = {
        "num_vertices": num_vertices,
        "depot": depot,
        "num_required_edges": num_required_edges,
        "num_non_required_edges": num_non_required_edges,
        "num_vehicles": num_vehicles,
        "capacity": capacity,
        "total_cost": total_cost,
        "graph": graph,
        "tasks": tasks
    }
    return info

    # return num_vertices, depot, \
    #     num_required_edges, num_non_required_edges, \
    #     num_vehicles, capacity, total_cost, \
    #     graph, tasks



def shortest_path(graph):
    n = graph.shape[0]
    sp = np.zeros_like(graph, dtype=int)
    sp.fill(MAX_COST)
    is_visited = np.zeros((n, ), dtype=bool)

    for src in range(n):
        is_visited.fill(False)
        heap = [(0, src)]  # (distance, point)
        sp[src, src] = 0  # 

        while len(heap) > 0:
            cost, s = heappop(heap)
            if is_visited[s]: continue
            is_visited[s] = True


            for d in range(n):
                # 没有被访问过
                new_cost = cost + graph[s, d]
                if not is_visited[d] and new_cost < sp[src, d]:
                    sp[src, d] = new_cost
                    
                    # 将d插入堆中
                    heappush(heap, (new_cost, d))

    return sp
