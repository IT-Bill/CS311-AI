from __future__ import annotations
from typing import List, Dict
import numpy as np
from heapq import heappop, heappush
import random
import operator
from random import choice, randint, choices, sample, shuffle, randrange
from time import perf_counter
from copy import deepcopy
MAX_COST = 1 << 31 - 1

#! Global variables
class gv:
    num_vehicles = None
    num_tasks = None
    task_dict: Dict[int, Task] = None
    sp = None  # shortest path
    capacity = None
    total_demand = None

    @staticmethod
    def init(info):
        gv.num_tasks = info["num_required_edges"]
        gv.task_dict = info["task_dict"]
        gv.sp = info["sp"]
        gv.num_vehicles = info["num_vehicles"]
        gv.capacity = info["capacity"]
        gv.total_demand = info["total_demand"]

#!####################################
#! CARP types

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
        if self.no == 0:
            return other.no == 0
        # return self.no == other.no or abs(self.no - other.no) == gv.num_tasks
        return self.no == other.no
    
    def __hash__(self) -> int:
        """两个方向的task视为同一个"""
        return self.no + self.invert_no

    def __repr__(self):
        # return f"no.{self.no}: ({self.s}, {self.t})"
        return f"({self.s}, {self.t}): {self.demand}"


class Route:
    def __init__(self, tasks=None, cost=0, remain_cap=None):
        """
        :param
          remain_cap: 这条路线还剩余多少容量
        """
        self.tasks: List[Task] = deepcopy(tasks) if tasks is not None else [gv.task_dict[0]]
        self.cost = cost
        self.remain_cap = remain_cap if remain_cap is not None else gv.capacity

    def append_cost(self, task: Task):
        return gv.sp[self.tasks[-1].t, task.s] + task.cost

    def append_task(self, task: Task):
        # assert self.remain_cap - task.demand >= 0  # 容量必须足够
        ac = self.append_cost(task)
        self.cost += ac
        self.remain_cap -= task.demand
        self.tasks.append(task)  # !最后才能加！！！不然-1就不是倒数第一个了

        # !DEBUG #######################
        if self.remain_cap < 0:
            assert False
        # !#############################

        return ac

    def insert_cost(self, idx, task: Task):
        """插入一个task需要增加多少cost"""
        # assert idx > 0  # 不能插在0位置，其实最后一个位置也不能插入(append)
        t1, t2 = self.tasks[idx - 1], self.tasks[idx]
        return gv.sp[t1.t, task.s] + task.cost + gv.sp[task.t, t2.s] - gv.sp[t1.t, t2.s]

    def insert_task(self, idx, task: Task):
        ic = self.insert_cost(idx, task)
        self.cost += ic
        self.remain_cap -= task.demand
        self.tasks.insert(idx, task)

        # !DEBUG #######################
        if self.remain_cap < 0:
            assert False
        # !#############################
        return ic

    def remove_cost(self, idx):
        """删除tasks[idx]会少多少cost"""
        t1 = self.tasks[idx - 1]
        t2 = self.tasks[idx]
        t3 = self.tasks[idx + 1]
        return gv.sp[t1.t, t2.s] + t2.cost + gv.sp[t2.t, t3.s] - gv.sp[t1.t, t3.s]

    def remove_task(self, task: Task=None, idx=None):
        # 当没有坐标的时候，就需要找到这个task的位置，再判断应该减去多少cost
        assert not (task is None and idx is None)
        if idx is None:
            idx = self.tasks.index(task)
        elif task is None:
            task = self.tasks[idx]
        
        rc = self.remove_cost(idx)  # 方便return
        self.cost -= rc
        self.remain_cap += task.demand
        self.tasks.pop(idx)
        return rc


    def addable(self, task: Task):
        return self.remain_cap - task.demand >= 0

    def __getitem__(self, idx):
        return self.tasks[idx]
    
    def __repr__(self):
        return str(self.__dict__)

    def __eq__(self, other: Route):
        if operator.eq(self.tasks, other.tasks):
            return True
        
        # 有可能是逆序
        inv_tasks = [task.invert_task for task in other.tasks]
        if operator.eq(self.tasks, inv_tasks):
            return True

        return False

    def __lt__(self, other):
        return self.cost -  other.cost

class Solution:
    def __init__(self, routes=[], cost=0):
        # ! 需要deepcopy，否则会一直在原来的列表上累加
        self.routes: List[Route] = deepcopy(routes)
        self.cost = cost

    def add_route(self, route: Route):
        self.routes.append(route)
        self.cost += route.cost

    def calc_cost(self):
        cost = 0
        for r in self.routes:
            cost += r.cost
        self.cost = cost
        return cost
    
    def feasible(self):
        """是否是可行的，需要看不同的任务数是否够"""
        tasks = []
        for r in self.routes:
            tasks += r.tasks
        return len(set(tasks)) - 1 == gv.num_tasks
    
    @classmethod
    def crossover(cls, s1, s2):
        s1r, s2r = s1.routes, s2.routes
        a, b = randint(0, len(s1r) - 1), randint(0, len(s2r) - 1)
        # print("crossover", a, b)

        # !!!!!!这里也要deepcopy...不然会影响原来的solution
        s0r = deepcopy(s1r[:a] + s1r[a + 1:])
        old_r, new_r = set(s1r[a]), set(s2r[b])

        common = old_r & new_r
        # duplicate可以不用double
        duplicated = list(new_r - common)
        # unserved必须double
        unserved = list(old_r - common)
        unserved = unserved + [task.invert_task for task in unserved]

        # !!!!!!!!!!!!!!!!!!!
        new_r = deepcopy(s2r[b])

        while len(duplicated) > 0:
            task = duplicated.pop()
            for route in s0r:
                if task in route.tasks:
                    
                    # 在这个route中找到了重复的task，从这个位置删除会少多少cost
                    # 这个是非crossover中重复的任务
                    i1 = route.tasks.index(task)
                    non_co = route.remove_cost(i1)
                    # 这个是crossover中重复的任务，也就是new_r route
                    i2 = new_r.tasks.index(task)
                    co = new_r.remove_cost(i2)

                    # print(task, i1, i2)
                    if non_co > co:
                        # 非crossover中重复的任务少的cost更多，因此移除
                        route.remove_task(task, i1)
                    
                    else:
                        new_r.remove_task(task, i2)
                    
                    # print(task)
                    # duplicated.remove(task)
                    # duplicated.remove(task.invert_task)
                    break

        # print()
        s0r.append(new_r)
        while len(unserved) > 0:
            task = unserved.pop()
            min_cost = MAX_COST
            insert_route, insert_idx = None, None
            for route in s0r:
                # 搜索每一条route，首先看看能否添加
                if route.addable(task):
                    # 容量够了，遍历这个路线的所有位置，看看cost如何
                    # 排除第一个，最后不用-1，不然只有两个dummy_task时插不进
                    for idx in range(1, len(route.tasks)):
                        cost = route.insert_cost(idx, task)
                        if cost < min_cost:
                            min_cost = cost  # ! ...
                            insert_route, insert_idx = route, idx
            
            if insert_route is not None:
                # 找到了可以插入的位置
                insert_route.insert_task(insert_idx, task)
                # 从unserved中移除反方向的task
                unserved.remove(task.invert_task)
            
            # print(task)
            
        
        new_solu = Solution(s0r)
        new_solu.calc_cost()
        return new_solu
    
    @classmethod
    def gene_solu(cls):
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

    @classmethod
    def init_pop(cls, pop_size):
        return [cls.gene_solu() for _ in range(pop_size)]
    
    def __repr__(self):
        s = "solution cost:{}, {}\n".format(self.cost, "feasible" if self.feasible() else "infeasible")
        for route in self.routes:
            s += str(route) + "\n"
        
        return s
    
    def __getitem__(self, idx):
        return self.routes[idx]
    
    def __eq__(self, other) -> bool:
        r1 = sorted(self.routes)
        r2 = sorted(other.routes)
        return operator.eq(r1, r2)
    
    def eval(self):
        """评估，越低越好"""
        # demand，剩余的越多分越高
        unserved_demand = gv.total_demand
        for route in self.routes:
            unserved_demand -= gv.capacity - route.remain_cap
        
        score = 0
        score += self.cost
        score += int(score * (unserved_demand * 1.5 / gv.total_demand))

        return score


  
#! ##########################
# Read file
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
    # total_demand = int(contents[7].split(":")[1])  

    graph = np.zeros((num_vertices, num_vertices), dtype=int)
    graph.fill(MAX_COST)
    task_dict = {0: Task(0, 0, 0, 0)}

    total_demand = 0
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
            total_demand += c[3]

    info = {
        "num_vertices": num_vertices,
        "depot": depot,
        "num_required_edges": num_required_edges,
        "num_non_required_edges": num_non_required_edges,
        "num_vehicles": num_vehicles,
        "capacity": capacity,
        "total_demand": total_demand,
        "sp": shortest_path(graph),
        "task_dict": task_dict
    }
    return info

#!###########################
# generate solutions and population
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


#!#######################################
# neighbor operation

def inversion(route: Route, idx):
    """翻转route中的一个task"""
    route = deepcopy(route)
    task = route[idx]
    change_cost = 0
    change_cost -= route.remove_task(task, idx)
    change_cost += route.insert_task(idx, task)
    return route


#!##################################
# utils
def update_pop(pop, solu):
    feasible_list = []
    infeasible_list = []
    for i in range(len(pop)):
        if pop[i].feasible():
            feasible_list.append(i)
        else:
            infeasible_list.append(i)
    
    
    # 保持feasible的比例在0.75以上
    if solu.feasible() or len(feasible_list) / len(pop) > 0.75:
        pop.append(solu)
        pop = sorted(pop, key=lambda x: x.cost)
        pop.pop()
        return pop
    else:
        best_infeasible = min(infeasible_list, key=lambda i: pop[i].cost)
        if pop[best_infeasible].cost > solu.cost:
            # 最好的infeasible都不如solu，换
            pop.pop(infeasible_list[0])
            pop.append(solu)
    
    return sorted(pop, key=lambda x: x.cost)
            

def best_feasible_solu(pop):
    """假设pop已经排好序"""
    for solu in pop:
        if solu.feasible():
            return solu
