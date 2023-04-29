import numpy as np
from heapq import heappop, heappush
from random import choice, randint

MAX_COST = int(1e9)

# !########################################################
# read file and calc shortest path
def read_file(path):
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
    tasks = {0: ((depot, depot), 0)}

    id = 1
    for c in contents[9: 9 + num_required_edges + num_non_required_edges]:
        c = [int(i) for i in c.split()]
        n1, n2 = c[0] - 1, c[1] - 1
        graph[n1, n2] = c[2]
        graph[n2, n1] = c[2]
        if c[3] != 0:
            # ! 两个方向都会放进去
            tasks[id] = ((n1, n2), c[3])
            tasks[id + num_required_edges] = ((n2, n1), c[3])
            id += 1

    info = {
        "num_vertices": num_vertices,
        "depot": depot,
        "num_required_edges": num_required_edges,
        "num_non_required_edges": num_non_required_edges,
        "num_vehicles": num_vehicles,
        "capacity": capacity,
        "total_cost": total_cost,
        "sp": shortest_path(graph),
        "tasks": tasks
    }
    return info

# !########################################################
# generate population
class Route:
    def __init__(self, remain_cap, task_ids) -> None:
        self.remain_cap = remain_cap
        self.task_ids = task_ids

    def remove_id(self, id, demand):
        self.remain_cap += demand
        self.task_ids.remove(id)
    
    def insert_id(self, insert_idx, id, demand):
        self.remain_cap -= demand
        self.task_ids.insert(insert_idx, id)
    



    def __repr__(self):
        return str(self.__dict__)

class Solution:
    def __init__(self, cost, routes) -> None:
        self.cost = cost
        # s = [Route, Route, ...]
        self.routes = routes

    def __repr__(self):
        return str(self.__dict__)


def gene_solu(**kwargs):
    sp, tasks, depot, capacity, num_vehicles = kwargs["sp"], kwargs["tasks"], kwargs["depot"], kwargs["capacity"], kwargs["num_vehicles"]

    # tasks 是 字典
    routes = []
    num_tasks = len(tasks) // 2  # 实际上有多少tasks
    # ! taskID, 不要放0！！
    unserved_ids = [i for i in range(1, len(tasks))]  
    cost = 0  # 这个solution的总花费
    
    for _ in range(num_vehicles):
        if len(unserved_ids) == 0:
            break
        
        remain_cap = capacity
        cur_vertex = depot  # 需要计算cost
        task_ids = [0]

        while True:
            valid_ids = []
            for id in unserved_ids:
                task = tasks[id]
                if task[1] <= remain_cap:
                    valid_ids.append(id)
            
            if len(valid_ids) == 0:
                break
            
            else:
                id = choice(valid_ids)
                task = tasks[id]

                task_ids.append(id)  # 路径中添加id
                remain_cap -= task[1]  # 减少容量
                # 累加cost
                cost += sp[task[0]] + sp[cur_vertex, task[0][0]]
                # 移除id
                unserved_ids.remove(id)
                if id <= num_tasks:
                    unserved_ids.remove(id + num_tasks)
                else:
                    unserved_ids.remove(id - num_tasks)
        
        task_ids.append(0)
        routes.append(Route(remain_cap, task_ids))
    
    return Solution(cost, routes)

def init_pop(pop_size, **kwargs):
    return [gene_solu(**kwargs) for _ in range(pop_size)]
                
# !########################################################