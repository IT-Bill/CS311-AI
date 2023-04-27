import numpy as np
from main import *
from copy import deepcopy
from random import choice


def rule1(sp, **kwargs):
    """maximize the distance from the head of task to the depot"""
    return max(kwargs["tasks"], key=lambda x: sp[kwargs["depot"], x[0][0]])

def rule2(sp, **kwargs):
    """minimize the distance from the head of task to the depot"""
    return min(kwargs["tasks"], key=lambda x: sp[kwargs["depot"], x[0][0]])

def rule3(sp, **kwargs):
    """maximize the term dem(t)/sc(t)"""
    return max(kwargs["tasks"], key=lambda x: x[1] / sp[x[0][0], x[0][1]])

def rule4(sp, **kwargs):
    """minimize the term dem(t)/sc(t)"""
    return min(kwargs["tasks"], key=lambda x: x[1] / sp[x[0][0], x[0][1]])

def rule5(sp, **kwargs):
    """use rule1 if the vehicle is less than half full, otherwise use rule2"""
    return rule1(sp, **kwargs) if kwargs["remain_cap"] / kwargs["capacity"] > 0.5 else rule2(sp, **kwargs)




def generate_route_by_rule(sp, tasks, depot, capacity, num_vehicles, rule):
    dummy_task = ((depot, depot), 0)
    route = []
    
    # 多辆车
    for _ in range(num_vehicles):
        if len(tasks) == 0:
            break

        remain_cap = capacity
        cur_vertex = depot
        r = []

        while len(tasks) > 0:
            valid_tasks = []
            for task in tasks:
                if task[1] <= remain_cap:
                    valid_tasks.append(task)

            if len(valid_tasks) == 0:
                # 没有有效的任务
                break

            elif len(valid_tasks) == 2:
                # 因为一个tasks有两条记录
                # 只有一个有效任务，最短路径过去
                task = valid_tasks[0] if valid_tasks[0][0][0] < valid_tasks[1][0][0] else valid_tasks[1]

                # 添加路线
                r.append(task)

                # 修改车的位置
                cur_vertex = task[0][0]  

                # 移除task
                tasks.remove(valid_tasks[0])
                tasks.remove(valid_tasks[1])

                # 减少容量
                remain_cap -= task[1]

                # 一定是最后一个了
                break

            else:
                # 有多个任务满足条件，选一个距离最短的
                min_dist = min(
                    valid_tasks, key=lambda x: sp[cur_vertex, x[0][0]])[1]
                # 检查是否有多个距离最短的点
                min_dist_tasks = [t for t in valid_tasks if t[1] == min_dist]
                if len(min_dist_tasks) == 1:  # 1，只有一个
                    task = min_dist_tasks[0]
                else:  # 多个，使用rule
                    task = rule(sp, depot=depot, tasks=tasks, 
                                capacity=capacity, remain_cap=remain_cap)
                
                r.append(task)
                cur_vertex = task[0][0]
                remain_cap -= task[1]
                tasks.remove(task)
                tasks.remove(((task[0][1], task[0][0]), task[1]))
        
        # 每辆车作为一个list
        route.append(r)
    
    return route


def generate_route_random(tasks, depot, capacity, num_vehicles):
    dummy_task = ((depot, depot), 0)
    route = []
    
    # 多辆车
    for _ in range(num_vehicles):
        if len(tasks) == 0:
            break

        remain_cap = capacity
        r = []

        while len(tasks) > 0:
            valid_tasks = []
            for task in tasks:
                if task[1] <= remain_cap:
                    valid_tasks.append(task)

            if len(valid_tasks) == 0:
                # 没有有效的任务
                break

            else:
                task = choice(valid_tasks)
                
                r.append(task)
                remain_cap -= task[1]
                tasks.remove(task)
                tasks.remove(((task[0][1], task[0][0]), task[1]))
        
        # 一辆车回到终点后，加入dummy_task
        route.append(r)
    
    return route


def generate_route(sp, tasks, depot, capacity, num_vehicles, num_routes):
    return [generate_route_by_rule(
        sp, deepcopy(tasks),
        depot, capacity, num_vehicles, rule)
        for rule in [rule1, rule2, rule3, rule4, rule5]] + \
        [generate_route_random(deepcopy(tasks), depot, 
                               capacity, num_vehicles) for _ in range(num_routes - 5)]




