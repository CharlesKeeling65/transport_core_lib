# -*- coding: utf-8 -*-
"""方法选择和时间估算相关函数"""
import math
import numpy as np
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


def calculate_dynamic_threshold(
    n_supply,
    n_demand,
    n_jobs=8,
    total_pixels=44102097,
    K=150.0,
    d_min=10,
    d_max=200,
):
    """
    基于成本模型交叉点的解析动态阈值。
    
    数学推导：
        T_traditional ≈ c1 × d × XY
        T_kdtree ≈ c2 × (S+D) × log(S+D) / n_jobs
        令 T_traditional = T_kdtree，解出：
        d* = (c2/c1) × (S+D) × log(S+D) / (XY × n_jobs)
           = K × density × log(S+D) / n_jobs
    
    参数：
        K: 机器校准常数，默认值 150 在典型硬件上适用。
           K 越小代表 KD-Tree 相对越快（如 MKL 加速的机器），
           K 越大代表传统法相对越快（如小缓存/慢内存的机器）。
        d_min: 下限保护，防止极端稀疏场景下阈值过低。
        d_max: 上限保护，防止极端密集场景下阈值过高。
    """
    total_points = n_supply + n_demand
    if total_points == 0 or total_pixels <= 0 or n_jobs <= 0:
        return d_min
    
    density = total_points / total_pixels
    log_n = math.log2(total_points) if total_points > 1 else 1.0
    
    d_star = K * density * log_n / max(n_jobs, 1)
    
    return int(np.clip(d_star, d_min, d_max))
