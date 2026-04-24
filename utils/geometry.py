# -*- coding: utf-8 -*-
"""几何计算相关函数"""
import math
import numpy as np


def direct_list(distance):
    """生成指定距离范围内的所有偏移量"""
    sqrt_2_div_2 = math.sqrt(2) / 2
    max_square_value = (distance + sqrt_2_div_2) ** 2
    min_square_value = (distance - 1 + sqrt_2_div_2) ** 2
    for dr in range(-distance, distance + 1):
        max_square = max_square_value - dr**2
        min_square = min_square_value - dr**2
        dc_max = int(np.sqrt(max_square))
        if min_square < 0:
            dc_min = 0
            for dc in range(-dc_max, dc_max + 1):
                yield dr, dc
        else:
            dc_min = int(math.ceil(math.sqrt(min_square)))
            for dc in list(range(-dc_max, -dc_min + 1)) + list(
                range(dc_min, dc_max + 1)
            ):
                yield dr, dc


def edges_line_func(p, n):
    """计算供应点和需求点的交集"""
    return np.where((p != 0) & (n != 0), 1, 0).astype(np.int8)


def move_array(arr, direct, max_distance):
    """移动数组"""
    di, dj = direct
    padded_arr = np.pad(arr, max_distance, mode="constant").astype(np.float32)
    moved_arr = np.roll(padded_arr, (di, dj), axis=(0, 1)).astype(np.float32)
    return moved_arr[max_distance:-max_distance, max_distance:-max_distance]


def calculate_distance_sq(row1, col1, row2, col2):
    """计算两点之间的距离平方"""
    dr = row1 - row2
    dc = col1 - col2
    return dr**2 + dc**2
