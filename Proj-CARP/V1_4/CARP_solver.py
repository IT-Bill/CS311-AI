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
    def __init__(self, no, s, t, cost, demand):
        self.no = no
        self.s = s
        self.t = t
        self.cost = cost
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

    # @property
    # def cost(self):
    #     return gv.sp[self.st]
    
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

    def output(self):
        if self.no == 0:
            return "0"
        return f"({self.s + 1},{self.t + 1})"

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

    def idx_task_or_inv_task(self, task: Task):
        if task in self.tasks:
            return self.tasks.index(task)
        elif task.invert_task in self.tasks:
            return self.tasks.index(task.invert_task)
        return None
    
    def calc_cost(self):
        sp = gv.sp
        cost = 0
        t = self.tasks
        for idx in range(1, len(t)):
            cost += t[idx].cost + sp[t[idx - 1].t, t[idx].s]
        self.cost = cost
        return cost
        

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

    def dcopy(self):
        r = Route(deepcopy(self.tasks), self.cost, self.remain_cap)
        return r
    
    def output(self):
        str_tasks = [task.output() for task in self.tasks]
        return ",".join(str_tasks)

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
            for t in r.tasks[1:-1]:
                tasks.append(t)
                tasks.append(t.invert_task)
        task_set = set(tasks)
        return len(tasks) == len(task_set) and len(tasks) / 2 == gv.num_tasks
    
    @classmethod
    def crossover(cls, s1: Solution, s2: Solution):
        # s1, s2 = s1.dcopy(), s2.dcopy()
        s1r, s2r = s1.routes, s2.routes
        a, b = randint(0, len(s1r) - 1), randint(0, len(s2r) - 1)
        # print("crossover", a, b)

        # !!!!!!这里也要deepcopy...不然会影响原来的solution
        s0r = deepcopy(s1r)
        s0r.pop(a)
        old_tasks, new_tasks = deepcopy(s1r[a].tasks), deepcopy(s2r[b].tasks)
        old_tasks += [task.invert_task for task in old_tasks]
        new_tasks += [task.invert_task for task in new_tasks]
        old_tasks = set(old_tasks)
        new_tasks = set(new_tasks)

        common = old_tasks & new_tasks
        # duplicate可以不用double
        duplicated = list(new_tasks - common)
        # unserved必须double
        unserved = list(old_tasks - common)
        
        # !!!!!!!!!!!!!!!!!!!
        new_r = deepcopy(s2r[b])

        while len(duplicated) > 0:
            task = duplicated.pop()
            for route in s0r:
                i1 = route.idx_task_or_inv_task(task)
                if i1 is not None:
                    
                    # 在这个route中找到了重复的task，从这个位置删除会少多少cost
                    # 这个是非crossover中重复的任务
                    non_co = route.remove_cost(i1)
                    # 这个是crossover中重复的任务，也就是new_r route
                    i2 = new_r.idx_task_or_inv_task(task)
                    co = new_r.remove_cost(i2)

                    # print(task, i1, i2)
                    if non_co > co:
                        # 非crossover中重复的任务少的cost更多，因此移除
                        route.remove_task(idx=i1)
                    
                    else:
                        new_r.remove_task(idx=i2)
                    
                    duplicated.remove(task.invert_task)
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
        # score += int(score * (unserved_demand * 1.5 / gv.total_demand))

        return score

    def assert_demand(self):
        served_demand_by_cap = 0
        for route in self.routes:
            served_demand_by_cap += gv.capacity - route.remain_cap
        
        tasks = []
        served_demand_by_task = 0
        for r in self.routes:
            for t in r.tasks[1:-1]:
                tasks.append(t)
                served_demand_by_task += t.demand

        assert len(tasks) == len(set(tasks))
        assert served_demand_by_task == served_demand_by_cap

    def dcopy(self):
        routes = [r.dcopy() for r in self.routes]
        s = Solution(routes, self.cost)
        return s
    
    def output(self):
        res = ""
        str_routes = [route.output() for route in self.routes]
        res += "s " + ",".join(str_routes)
        res += "\nq " + str(self.cost)
        return res
  
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
    task_dict = {0: Task(0, 0, 0, 0, 0)}

    total_demand = 0
    id = 1
    for c in contents[9: 9 + num_required_edges + num_non_required_edges]:
        c = [int(i) for i in c.split()]
        n1, n2 = c[0] - 1, c[1] - 1
        graph[n1, n2] = c[2]
        graph[n2, n1] = c[2]
        if c[3] != 0:
            # ! 两个方向都会放进去
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # ! 任务初始化的时候，用的不是算出来的最短路径，因为可能有其他的路径比直达更短！！！
            task_dict[id] = Task(id, n1, n2, c[2], c[3])
            task_dict[id + num_required_edges] = Task(id + num_required_edges, n2, n1, c[2], c[3])
            total_demand += c[3]
            id += 1
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

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
        
        route = Route()  # 初始有一个0号
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
                # 使用类似path-scanning的方法，但是随机选取
                # min_deadhead = MAX_COST
                # min_deadhead_tasks = []
                # for task in valid_tasks:
                #     deadhead = gv.sp[route.tasks[-1].t, task.s]
                #     if deadhead < min_deadhead:
                #         min_deadhead_tasks = [task]
                #     elif deadhead == min_deadhead:
                #         min_deadhead_tasks.append(task)
                
                # task = choice(min_deadhead_tasks)
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

# def inversion(solu: Solution):
#     """翻转route中的一个task"""
    

#     route = deepcopy(route)
#     task = route[idx]
#     change_cost = 0
#     change_cost -= route.remove_task(task, idx)
#     change_cost += route.insert_task(idx, task)
#     return route


#!##################################
def best_feasible_solu(pop):
    """假设pop已经排好序"""
    pop = sorted(pop, key=lambda solu: solu.cost)
    for solu in pop:
        if solu.feasible():
            return solu

def single_insert(init_solu: Solution, best_cost, tabu_list, max_try):
    init_solu = init_solu.dcopy()
    
    best_neighbor = None
    while True:
        remove_route_idx = randint(0, len(init_solu.routes) - 1)
        l = len(init_solu[remove_route_idx].tasks)
        if l > 2:  # 不是只有两个dummy task
            remove_task_idx = randint(1, l - 2)
            break
    task = init_solu[remove_route_idx][remove_task_idx]  # 这个是焦点，被remove的task
    
    init_solu[remove_route_idx].remove_task(idx=remove_task_idx)


    num_try = 0
    for _ in range(max_try):
        if num_try >= max_try:
            break
        
        # print(num_try, end=" ")
        insert_route_idx, insert_task_idx = None, None
        while num_try < max_try:
            # 选一个被插入的路线
            #!!!!!!!这个deepcopy要放在这里！！！！！
            solu = init_solu.dcopy()
            insert_route_idx = randint(0, len(solu.routes) - 1)
            # ! DEBUG
            if len(solu.routes[insert_route_idx].tasks) == 2:
                a = 1
            # ! DEBUG

            insert_task_idx =  randint(1, len(solu[insert_route_idx].tasks) - 1)
            num_try += 1 # 尝试次数+1

            if (remove_route_idx, remove_task_idx) != (insert_route_idx, insert_task_idx) \
                and solu[insert_route_idx].addable(task):  # 是要判断remove task能否被加入

                # 这个位置可以insert
                
                # 尝试插入
                insert_route = solu[insert_route_idx]
                inv_task = task.invert_task

                insert_task_cost = insert_route.insert_task(insert_task_idx, task)
                # 看看是否出现重复解
                if solu in tabu_list:
                    insert_task_cost = MAX_COST
                insert_route.remove_task(idx=insert_task_idx) # 恢复
                
                inv_task_cost = insert_route.insert_task(insert_task_idx, inv_task)
                if solu in tabu_list:
                    inv_task_cost = MAX_COST
                insert_route.remove_task(idx=insert_task_idx) # 恢复

                if insert_task_cost == MAX_COST and inv_task_cost == MAX_COST:
                    # 说明两个方向的task都在禁忌表里，不能插入
                    continue # 开始下一次try
                
                elif insert_task_cost < inv_task_cost:
                    insert_route.insert_task(insert_task_idx, task)
                
                else:
                    insert_route.insert_task(insert_task_idx, inv_task)
            
                # 判断是否比原来的解更加好
                solu.calc_cost()
                if solu.cost < best_cost:
                    best_cost = solu.cost
                    best_neighbor = solu
        
    return best_neighbor


def merge_split(solu: Solution):
    solu = solu.dcopy()

    sp = gv.sp
    task_dict = gv.task_dict
    dummy_task = task_dict[0]
    depot = dummy_task.s

    def rule1(**kwargs):
        """maximize the distance from the head of task to the depot"""
        return max(kwargs["tasks"], key=lambda task: sp[depot, task.s])

    def rule2(**kwargs):
        """minimize the distance from the head of task to the depot"""
        return min(kwargs["tasks"], key=lambda task: sp[depot, task.s])

    def rule3(**kwargs):
        """maximize the term dem(t)/sc(t)"""
        return max(kwargs["tasks"], key=lambda task: task.demand / sp[task.st])

    def rule4(**kwargs):
        """minimize the term dem(t)/sc(t)"""
        return min(kwargs["tasks"], key=lambda task: task.demand / sp[task.st])

    def rule5(**kwargs):
        """use rule1 if the vehicle is less than half full, otherwise use rule2"""
        return rule1(**kwargs) if kwargs["remain_cap"] / gv.capacity > 0.5 else rule2(**kwargs)

    def _ms(tasks, rule):
        new_routes = [Route(), Route()]
        tasks = deepcopy(tasks)
        for route in new_routes:
            
            while True:
                valid_tasks = [task for task in tasks if route.addable(task)]
                
                if len(valid_tasks) == 0:
                    break
                    
                else:
                    # 有至少一个任务可以加入这条route，计算最短距离

                    min_deadhead = MAX_COST
                    min_deadhead_tasks = []
                    for task in valid_tasks:
                        deadhead = gv.sp[route.tasks[-1].t, task.s]
                        if deadhead < min_deadhead:
                            min_deadhead = deadhead
                            min_deadhead_tasks = [task]
                        elif deadhead == min_deadhead:
                            min_deadhead_tasks.append(task)
                    
                    # min_deadhead_tasks的deadhead都相同且最小
                    if len(min_deadhead_tasks) == 1:
                        task = min_deadhead_tasks[0]
                    else: # 多个，使用rule
                        # !!!!!!! tasks = min_dist_tasks，不是tasks !!!!!!!!!!!
                        task = rule(tasks=valid_tasks, remain_cap=route.remain_cap)
                    
                    route.append_task(task)
                    tasks.remove(task)
                    tasks.remove(task.invert_task)
            
            route.append_task(dummy_task)
        
        return new_routes
    

    # 选择两条路线进行merge split
    routes1 = solu.routes.pop(randint(0, len(solu.routes)) - 1)
    routes2 = solu.routes.pop(randint(0, len(solu.routes)) - 1)

    unserved_tasks = [task for task in routes1.tasks] + [task for task in routes2.tasks]
    # ! 不要遗漏反方向的
    unserved_tasks += [task.invert_task for task in unserved_tasks]
    unserved_tasks = set(unserved_tasks)
    unserved_tasks.remove(dummy_task)
    unserved_tasks = list(unserved_tasks) # 去重，同时去掉dummy_task再变回list
    shuffle(unserved_tasks)

    # 一共有五种，每种里有2条路线
    new_routes_list = [_ms(unserved_tasks, rule) for rule in [rule1, rule2, rule3, rule4, rule5]]
    
    best_routes = min(new_routes_list, key=lambda routes: routes[0].cost + routes[1].cost)

    # 在solution中加回这两条路线
    solu.add_route(best_routes[0])
    solu.add_route(best_routes[1])
    solu.calc_cost()
    return solu


def update_pop(pop, solu):
    feasible_list = []
    infeasible_list = []
    pop = deepcopy(pop)
    for i in range(len(pop)):
        if pop[i].feasible():
            feasible_list.append(i)
        else:
            infeasible_list.append(i)
    
    
    # 保持feasible的比例在0.75以上
    if solu.feasible() or len(feasible_list) / len(pop) > 0.75:
        pop.append(solu)
        pop = sorted(pop, key=lambda x: x.eval())
        pop.pop()
        return pop
    else:
        best_infeasible = min(infeasible_list, key=lambda i: pop[i].eval())
        if pop[best_infeasible].eval() > solu.eval():
            # 最好的infeasible都不如solu，换
            pop.pop(infeasible_list[0])
            pop.append(solu)
    
    return sorted(pop, key=lambda x: x.eval())


def main(pop_size, seed, timeout, info):
    gv.init(info)

    random.seed(seed)

    pop = init_pop(pop_size)
    best_solu = min(pop, key=lambda x: x.eval())
    best_eval = best_solu.eval()
    tabu_list = []
    max_len_tabu = 30

    start = end = perf_counter()
    while end - start < timeout:
        # crossover
        co = sample(pop, k=2)
        new_solu = Solution.crossover(co[0], co[1])

        # 生成一个随机数，判断应该进行怎样improve
        ty = randint(0, 2)
        if ty == 0:
            pass
        elif ty == 1:
            # single insertion
            new_solu = single_insert(new_solu, best_eval, tabu_list, 10)
            pass

        
        elif ty == 2:
            # merge split
            best_ms_solu = new_solu
            for i in range(5):
                ms_solu = merge_split(new_solu.dcopy())
                if new_solu.eval() < best_ms_solu.eval():
                    best_ms_solu = ms_solu.dcopy()
            new_solu = best_ms_solu.dcopy()

        
        if new_solu is not None and new_solu not in pop and new_solu not in tabu_list:
            pop = update_pop(pop, new_solu)
            # new_solu.assert_demand()
        
            tabu_list.append(new_solu)

        bfs = best_feasible_solu(pop)
        eval = bfs.eval()
        if eval < best_eval:
            best_eval = eval
            # print(eval)

        # 删除禁忌表中留存时间过长的解
        if len(tabu_list) >= max_len_tabu:
            tabu_list.pop(0)

        end = perf_counter()
    
    return best_feasible_solu(pop)


if __name__ == "__main__":
    from getopt import getopt
    import sys
    import multiprocessing
    args = getopt(sys.argv, "-s:-t:")[1]
    file_path = args[1]
    timeout = int(args[3])
    seed = int(args[5])

    # !debug
    # file_path = "P:\CS311-AI\Proj-CARP\V1_2\sample1.dat"
    # timeout = 10
    # seed = 10
    # !####
    info = read_file(file_path)
    gv.init(info)

    args_list = [(15, seed + i, timeout - 2, info) for i in range(8)]
    pool = multiprocessing.Pool(8).starmap(main, args_list)
    # print(pool)
    # result = main(15, seed, timeout - 2)
    # print(result.output())

    best = min(pool, key=lambda solu: solu.cost)
    print(best.output())

"""
cd Proj-CARP\V1_4 && python .\CARP_solver.py ../datasets/egl-e1-A.dat -t 60 -s 5037913

"""

