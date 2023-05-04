from __future__ import annotations
from typing import List, Dict
import numpy as np
from heapq import heappop, heappush
import random
from random import choice, randint
from copy import deepcopy
MAX_COST = 1 << 31 - 1

class gv:
    num_vehicles = None
    num_tasks = None
    task_dict: Dict[int, Task] = None
    sp = None  # shortest path
    capacity = None

    @staticmethod
    def init(info):
        gv.num_tasks = info["num_required_edges"]
        gv.task_dict = info["task_dict"]
        gv.sp = info["sp"]
        gv.num_vehicles = info["num_vehicles"]
        gv.capacity = info["capacity"]




class Task:
    # ! 这是不包括重复的task和0号
    def __init__(self, no, s, t, demand):
        self.no = no
        self.s = s
        self.t = t
        self.demand = demand

    @property
    def st(self):
        """返回坐标"""
        return (self.s, self.t)

    @property
    def invert_no(self):
        if self.no == 0:
            return 0
        elif self.no <= gv.num_tasks:
            return self.no + gv.num_tasks
        else:
            return self.no - gv.num_tasks
    
    @property
    def invert_task(self):
        return gv.task_dict[self.invert_no]

    @property
    def cost(self):
        return gv.sp[self.st]
    
    def __eq__(self, other: Task):
        return self.no == other.no or abs(self.no - other.no) == gv.num_tasks
    
    def __repr__(self):
        # return f"no.{self.no}: ({self.s}, {self.t})"
        return f"({self.s}, {self.t}): {self.cost} {self.demand}"


class Route:
    def __init__(self, tasks=list(), cost=0, remain_cap=gv.capacity):
        """
        :param
          remain_cap: 这条路线还剩余多少容量
        """
        self.tasks: List[Task] = deepcopy(tasks)
        self.cost = cost
        self.remain_cap = remain_cap

    def append_cost(self, task: Task):
        return gv.sp[self.tasks[-1].t, task.s] + task.cost

    def append_task(self, task: Task):
        # assert self.remain_cap - task.demand >= 0  # 容量必须足够
        self.cost += self.append_cost(task)
        self.remain_cap -= task.demand
        self.tasks.append(task)  # !最后才能加！！！不然-1就不是倒数第一个了

    def insert_cost(self, idx, task: Task):
        """插入一个task需要增加多少cost"""
        # assert idx > 0  # 不能插在0位置，其实最后一个位置也不能插入(append)
        t1, t2 = self.tasks[idx - 1], self.tasks[idx]
        return gv.sp[t1.t, task.s] + task.cost + gv.sp[task.t, t2.s] - gv.sp[t1.t, t2.s]

    def insert_task(self, idx, task: Task):
        self.cost += self.insert_cost(idx, task)
        self.remain_cap -= task.demand
        self.tasks.insert(idx, task)

    def remove_task(self, task: Task, idx=None):
        # 当没有坐标的时候，就需要找到这个task的位置，再判断应该减去多少cost
        idx = self.tasks.index(task) if idx is None else idx
        self.cost -= self.insert_cost(idx, task)
        self.remain_cap += task.demand
        self.tasks.pop(idx)

    def addable(self, task: Task):
        return self.remain_cap - task.demand >= 0

    def __getitem__(self, idx):
        return self.tasks[idx]
    
    def __repr__(self):
        return str(self.__dict__)
    

class Solution:
    def __init__(self, routes=[], cost=0):
        # ! 需要deepcopy，否则会一直在原来的列表上累加
        self.routes: List[Route] = deepcopy(routes)
        self.cost = cost

    def add_route(self, route: Route):
        self.routes.append(route)
        self.cost += route.cost

    def __repr__(self):
        s = f"solution cost:{self.cost}\n"
        for route in self.routes:
            s += str(route) + "\n"
        
        return s
            

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
    task_dict = {0: Task(0, 0, 0, 0)}

    id = 1
    for c in contents[9: 9 + num_required_edges + num_non_required_edges]:
        c = [int(i) for i in c.split()]
        n1, n2 = c[0] - 1, c[1] - 1
        graph[n1, n2] = c[2]
        graph[n2, n1] = c[2]
        if c[3] != 0:
            # ! 两个方向都会放进去
            task_dict[id] = Task(id, n1, n2, c[3])
            task_dict[id + num_required_edges] = Task(id + num_required_edges, n2, n1, c[3])
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
        "task_dict": task_dict
    }
    return info


def gene_solu():
    task_dict, num_vehicles = gv.task_dict, gv.num_vehicles
    
    unserved_no = [i for i in range(1, gv.num_tasks * 2 + 1)]
    solu = Solution()
    dummy_task = task_dict[0]
    for _ in range(num_vehicles):
        if len(unserved_no) == 0:
            break
        
        route = Route(tasks=[dummy_task], remain_cap=gv.capacity)  # 初始有一个0号
        # 下面的循环生成一条route
        while True:
            valid_tasks = []
            for no in unserved_no:
                task = task_dict[no]
                if route.addable(task):
                    valid_tasks.append(task)
                
            if len(valid_tasks) == 0:
                break
                
            else: 
                task = choice(valid_tasks)
                route.append_task(task)

                unserved_no.remove(task.no)
                unserved_no.remove(task.invert_no)
        
        route.append_task(dummy_task)
        solu.add_route(route)
    
    return solu

def init_pop(pop_size):
    return [gene_solu() for _ in range(pop_size)]