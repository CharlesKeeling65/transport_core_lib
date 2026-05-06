# -*- coding: utf-8 -*-
"""网格分块相关函数"""
import numpy as np
import logging


def get_adaptive_grid_chunks(
    supply_rows,
    supply_cols,
    demand_rows,
    demand_cols,
    X,
    Y,
    distance,
    n_jobs,
    max_points_per_chunk=50000,
    max_mem_per_chunk=2 * 1024**3,  # 2GB
    min_grid_size=None,
):
    """自适应网格分块，递归细分大格子，预估内存，防止单块OOM"""
    if min_grid_size is None:
        min_grid_size = max(distance, distance)  # 至少等于 distance，保证 halo 完整覆盖搜索半径
    
    grid_size = max(distance // 2, min_grid_size)
    density_grid = np.zeros((X // grid_size + 1, Y // grid_size + 1), dtype=np.int32)
    supply_grid_pos = (supply_rows // grid_size, supply_cols // grid_size)
    demand_grid_pos = (demand_rows // grid_size, demand_cols // grid_size)
    for r, c in zip(*supply_grid_pos):
        if 0 <= r < density_grid.shape[0] and 0 <= c < density_grid.shape[1]:
            density_grid[r, c] += 1
    for r, c in zip(*demand_grid_pos):
        if 0 <= r < density_grid.shape[0] and 0 <= c < density_grid.shape[1]:
            density_grid[r, c] += 1
    total_points = len(supply_rows) + len(demand_rows)
    target_points_per_chunk = total_points // (n_jobs * 4)
    grid_chunks = []
    current_points = 0
    start_r = 0
    start_c = 0
    n_grid_rows = density_grid.shape[0]
    n_grid_cols = density_grid.shape[1]
    for r in range(n_grid_rows):
        for c in range(n_grid_cols):
            current_points += density_grid[r, c]
            if (
                current_points >= target_points_per_chunk
                or c == n_grid_cols - 1
                or (r == n_grid_rows - 1 and c == n_grid_cols - 1)
            ):
                if current_points > 0:
                    grid_chunks.append((start_r, r + 1, start_c, c + 1))
                current_points = 0
                start_c = c + 1
                if c == n_grid_cols - 1:
                    start_r = r + 1
                    start_c = 0

    # 递归细分大格子，考虑内存
    def chunk_too_big(chunk):
        r0, r1, c0, c1 = chunk
        supply_mask = (
            (supply_grid_pos[0] >= r0)
            & (supply_grid_pos[0] < r1)
            & (supply_grid_pos[1] >= c0)
            & (supply_grid_pos[1] < c1)
        )
        demand_mask = (
            (demand_grid_pos[0] >= r0)
            & (demand_grid_pos[0] < r1)
            & (demand_grid_pos[1] >= c0)
            & (demand_grid_pos[1] < c1)
        )
        supply_count = np.count_nonzero(supply_mask)
        demand_count = np.count_nonzero(demand_mask)
        mem_est = supply_count * demand_count * 4  # float32
        if mem_est > max_mem_per_chunk:
            logging.warning(
                f"Chunk ({r0},{r1},{c0},{c1}) estimated memory {mem_est/1024**3:.2f}GB, splitting further."
            )
        return (
            (supply_count > max_points_per_chunk)
            or (demand_count > max_points_per_chunk)
            or (mem_est > max_mem_per_chunk)
        )

    def split_chunk(chunk):
        r0, r1, c0, c1 = chunk
        rmid = (r0 + r1) // 2
        cmid = (c0 + c1) // 2
        # 优先按行切分，再按列
        if r1 - r0 > 1:
            return [(r0, rmid, c0, c1), (rmid, r1, c0, c1)]
        elif c1 - c0 > 1:
            return [(r0, r1, c0, cmid), (r0, r1, cmid, c1)]
        else:
            return [chunk]

    final_chunks = []
    stack = list(grid_chunks)
    while stack:
        chunk = stack.pop()
        if chunk_too_big(chunk):
            sub_chunks = split_chunk(chunk)
            if len(sub_chunks) == 1:
                final_chunks.append(chunk)
            else:
                stack.extend(sub_chunks)
        else:
            final_chunks.append(chunk)
    return final_chunks, grid_size
