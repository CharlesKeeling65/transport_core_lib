# -*- coding: utf-8 -*-
"""处理网格块的相关函数"""
import numpy as np
from scipy.spatial import cKDTree
from .geometry import calculate_distance_sq


def process_supply_chunk(
    s_start, s_end, p_raster, n_raster, distance, Y, demand_chunk_size
):
    """处理单个供应点块的辅助函数，使用网格加速"""
    X = p_raster.shape[0]
    supply_rows, supply_cols = np.nonzero(p_raster)
    demand_rows, demand_cols = np.nonzero(n_raster)

    sqrt_2_div_2 = np.sqrt(2) / 2
    max_sq = (distance + sqrt_2_div_2) ** 2
    min_sq = (distance - 1 + sqrt_2_div_2) ** 2

    # 获取当前块的供应点
    supply_chunk_rows = supply_rows[s_start:s_end]
    supply_chunk_cols = supply_cols[s_start:s_end]

    # 使用网格进行预筛选
    grid_size = distance  # 网格大小设为distance
    supply_grid_rows = supply_chunk_rows // grid_size
    supply_grid_cols = supply_chunk_cols // grid_size

    all_rows = []
    all_cols = []
    current_col = 0

    # 对每个供应点进行处理
    for i, (s_r, s_c) in enumerate(zip(supply_chunk_rows, supply_chunk_cols)):
        # 计算当前供应点所在的网格范围
        min_grid_r = max(0, (s_r - distance) // grid_size)
        max_grid_r = min((X - 1) // grid_size, (s_r + distance) // grid_size)
        min_grid_c = max(0, (s_c - distance) // grid_size)
        max_grid_c = min((Y - 1) // grid_size, (s_c + distance) // grid_size)

        # 筛选出在网格范围内的需求点
        demand_in_range = []
        for d_r, d_c in zip(demand_rows, demand_cols):
            d_grid_r = d_r // grid_size
            d_grid_c = d_c // grid_size
            if (
                min_grid_r <= d_grid_r <= max_grid_r
                and min_grid_c <= d_grid_c <= max_grid_c
            ):
                # 精确计算距离
                dist_sq = (d_r - s_r) ** 2 + (d_c - s_c) ** 2
                if min_sq <= dist_sq <= max_sq:
                    demand_in_range.append((d_r, d_c))

        # 为每个需求点创建边
        for d_r, d_c in demand_in_range:
            source_idx = s_r * Y + s_c
            target_idx = d_r * Y + d_c
            all_rows.extend([target_idx, source_idx])
            all_cols.extend([current_col, current_col])
            current_col += 1

    return all_rows, all_cols, current_col


def process_grid_chunk_v2(
    grid_bounds,
    p_raster,
    n_raster,
    distance,
    Y,
    supply_chunk_size=20000,
    demand_chunk_size=20000,
):
    """处理单个网格块的函数，使用 KD-Tree 优化"""
    r0, r1, c0, c1 = grid_bounds

    # 提取网格内的供应点和需求点
    supply_rows, supply_cols = np.nonzero(p_raster)
    demand_rows, demand_cols = np.nonzero(n_raster)

    # 筛选出在当前网格内的供应点和需求点
    supply_mask = (
        (supply_rows >= r0 * distance)
        & (supply_rows < r1 * distance)
        & (supply_cols >= c0 * distance)
        & (supply_cols < c1 * distance)
    )
    demand_mask = (
        (demand_rows >= r0 * distance)
        & (demand_rows < r1 * distance)
        & (demand_cols >= c0 * distance)
        & (demand_cols < c1 * distance)
    )

    grid_supply_rows = supply_rows[supply_mask]
    grid_supply_cols = supply_cols[supply_mask]
    grid_demand_rows = demand_rows[demand_mask]
    grid_demand_cols = demand_cols[demand_mask]

    # 如果网格内没有供应点或需求点，直接返回空结果
    if len(grid_supply_rows) == 0 or len(grid_demand_rows) == 0:
        return [], [], 0

    # 计算距离阈值的平方
    sqrt_2_div_2 = np.sqrt(2) / 2
    max_radius = distance + sqrt_2_div_2
    min_radius = distance - 1 + sqrt_2_div_2

    all_rows = []
    all_cols = []
    current_col = 0

    # 准备坐标数据用于 KD-Tree
    demand_coords = np.column_stack((grid_demand_rows, grid_demand_cols))
    supply_coords = np.column_stack((grid_supply_rows, grid_supply_cols))

    # 构建 KD-Tree (对需求点进行索引)
    tree = cKDTree(demand_coords)

    # 执行半径查询
    # query_ball_point 返回的是需求点在 grid_demand_rows 中的索引
    idx_outer = tree.query_ball_point(supply_coords, max_radius)
    idx_inner = tree.query_ball_point(supply_coords, min_radius)

    # 处理结果，过滤出圆环区域 (min_radius, max_radius]
    for i, (out_set, in_set) in enumerate(zip(idx_outer, idx_inner)):
        # 使用 set 减法获取圆环内的点索引
        ring_indices = set(out_set) - set(in_set)
        
        s_r, s_c = grid_supply_rows[i], grid_supply_cols[i]
        source_idx = s_r * Y + s_c
        
        for d_idx in ring_indices:
            d_r, d_c = grid_demand_rows[d_idx], grid_demand_cols[d_idx]
            target_idx = d_r * Y + d_c
            
            all_rows.extend([target_idx, source_idx])
            all_cols.extend([current_col, current_col])
            current_col += 1

    return all_rows, all_cols, current_col


def process_grid_chunk(
    grid_bounds,
    p_raster,
    n_raster,
    distance,
    Y,
    supply_chunk_size=20000,
    demand_chunk_size=20000,
):
    """处理单个网格块的函数，直接返回结果，避免临时文件I/O"""
    X = p_raster.shape[0]
    r0, r1, c0, c1 = grid_bounds

    # 提取网格内的供应点和需求点
    supply_rows, supply_cols = np.nonzero(p_raster)
    demand_rows, demand_cols = np.nonzero(n_raster)

    # 筛选出在当前网格内的供应点和需求点
    supply_mask = (
        (supply_rows >= r0 * distance)
        & (supply_rows < r1 * distance)
        & (supply_cols >= c0 * distance)
        & (supply_cols < c1 * distance)
    )
    demand_mask = (
        (demand_rows >= r0 * distance)
        & (demand_rows < r1 * distance)
        & (demand_cols >= c0 * distance)
        & (demand_cols < c1 * distance)
    )

    grid_supply_rows = supply_rows[supply_mask]
    grid_supply_cols = supply_cols[supply_mask]
    grid_demand_rows = demand_rows[demand_mask]
    grid_demand_cols = demand_cols[demand_mask]

    # 如果网格内没有供应点或需求点，直接返回空结果
    if len(grid_supply_rows) == 0 or len(grid_demand_rows) == 0:
        return [], [], 0

    # 计算距离阈值的平方
    sqrt_2_div_2 = np.sqrt(2) / 2
    max_sq = (distance + sqrt_2_div_2) ** 2
    min_sq = (distance - 1 + sqrt_2_div_2) ** 2

    all_rows = []
    all_cols = []
    current_col = 0

    # 直接计算网格内的供应点和需求点之间的距离
    for s_r, s_c in zip(grid_supply_rows, grid_supply_cols):
        for d_r, d_c in zip(grid_demand_rows, grid_demand_cols):
            dist_sq = calculate_distance_sq(s_r, s_c, d_r, d_c)
            if min_sq <= dist_sq <= max_sq:
                source_idx = s_r * Y + s_c
                target_idx = d_r * Y + d_c
                all_rows.extend([target_idx, source_idx])
                all_cols.extend([current_col, current_col])
                current_col += 1

    return all_rows, all_cols, current_col
