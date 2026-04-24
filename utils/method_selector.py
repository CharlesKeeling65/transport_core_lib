# -*- coding: utf-8 -*-
"""方法选择和时间估算相关函数"""
import math
from .geometry import direct_list


def estimate_traditional_method_time(distance, n_supply, n_demand):
    """估算传统方法的执行时间"""
    sqrt_2_div_2 = math.sqrt(2) / 2
    max_sq = (distance + sqrt_2_div_2) ** 2
    min_sq = (distance - 1 + sqrt_2_div_2) ** 2
    n_offsets = sum(1 for _ in direct_list(distance))
    time_per_offset = n_supply * n_demand / 1000000
    return n_offsets * time_per_offset


def estimate_adaptive_method_time(distance, n_supply, n_demand, n_jobs):
    """估算自适应网格方法 (基于 KD-Tree) 的执行时间"""
    total_points = n_supply + n_demand
    if total_points == 0:
        return 0
    
    # KD-Tree 的复杂度大致为 O(N log N)
    # 这里的常数项需要根据实际机器性能微调，1e-6 是一个假设的 Python/Scipy 转换系数
    log_n = math.log2(total_points) if total_points > 1 else 1
    complexity = total_points * log_n
    
    # 考虑到并行化效率 (n_jobs)
    # 并行效率通常不是 100%，取 0.8 的系数
    parallel_efficiency = 0.8
    estimated_time = (complexity * 1e-6) / (n_jobs * parallel_efficiency)
    
    return estimated_time


def calculate_dynamic_threshold(n_supply, n_demand, n_jobs=8, total_pixels=44102097):
    """根据数据密度动态计算分界点 (已针对 KD-Tree 优化进行调整)"""
    total_points = n_supply + n_demand
    density = total_points / total_pixels
    # 引入 KD-Tree 后，自适应网格法在大距离下优势更明显，下调切换阈值
    base_threshold = 40 
    if density < 0.1:
        return int(base_threshold * 0.8)
    elif density < 0.3:
        return int(base_threshold * 1.0)
    elif density < 0.5:
        return int(base_threshold * 1.2)
    else:
        return int(base_threshold * 1.5)
