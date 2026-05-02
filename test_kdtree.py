# -*- coding: utf-8 -*-
import numpy as np
import time
from utils.process import process_grid_chunk, process_grid_chunk_v2

def test_kdtree_consistency():
    print("Starting Consistency and Performance Test...")
    
    # 模拟数据
    X, Y = 1000, 1000
    distance = 50
    # 注意：grid_bounds 是以 distance 为单位的网格坐标
    # 如果 grid_bounds = (0, 1, 0, 1)，则实际像素范围是 [0, 50)
    # 但我们的点放在了 (25, 25) 和 (25+50, 25)，后者已经超出了网格范围！
    grid_bounds = (0, 5, 0, 5) 
    
    # 创建稀疏栅格数据
    p_raster = np.zeros((X, Y))
    n_raster = np.zeros((X, Y))
    
    # 随机生成一些点，确保落在圆环内
    np.random.seed(42)
    # 供应点放在中心附近
    s_rows = np.random.randint(100, 400, 2000)
    s_cols = np.random.randint(100, 400, 2000)
    p_raster[s_rows, s_cols] = 100
    
    # 需求点放在圆环附近 (distance=50)
    # x = r*cos(theta), y = r*sin(theta)
    thetas = np.random.uniform(0, 2*np.pi, 50000)
    rs = np.random.uniform(distance-0.5, distance+0.5, 50000)
    d_rows = (250 + rs * np.cos(thetas)).astype(int)
    d_cols = (250 + rs * np.sin(thetas)).astype(int)
    # 过滤掉越界的点
    mask = (d_rows >= 0) & (d_rows < X) & (d_cols >= 0) & (d_cols < Y)
    n_raster[d_rows[mask], d_cols[mask]] = 100
    
    # 手动添加几个绝对命中的点
    p_raster[250, 250] = 100
    n_raster[250+50, 250] = 100 
    n_raster[250, 250+50] = 100
    
    # 打印距离计算结果用于调试
    sqrt_2_div_2 = np.sqrt(2) / 2
    max_sq = (distance + sqrt_2_div_2) ** 2
    min_sq = (distance - 1 + sqrt_2_div_2) ** 2
    actual_dist_sq = (50)**2
    print(f"DEBUG: distance={distance}, min_sq={min_sq:.2f}, actual_sq={actual_dist_sq:.2f}, max_sq={max_sq:.2f}")
    print(f"DEBUG: IS WITHIN? {min_sq <= actual_dist_sq <= max_sq}")
    
    # 打印一些计算出的距离，调试为什么是0
    print(f"Sample distance check: sqrt((25+50-25)^2 + (25-25)^2) = {np.sqrt(50**2)}")
    
    print(f"Points in grid: Supply={np.count_nonzero(p_raster)}, Demand={np.count_nonzero(n_raster)}")
    
    # 运行原方法
    start_time = time.time()
    rows1, cols1, count1 = process_grid_chunk(grid_bounds, p_raster, n_raster, distance, distance, Y)
    time1 = time.time() - start_time
    print(f"Original method: {count1} edges found, time: {time1:.4f}s")
    
    # 运行 KD-Tree 优化方法
    start_time = time.time()
    rows2, cols2, count2 = process_grid_chunk_v2(grid_bounds, p_raster, n_raster, distance, distance, Y)
    time2 = time.time() - start_time
    print(f"KD-Tree method: {count2} edges found, time: {time2:.4f}s")
    
    # 验证一致性
    # 将结果转换为 set 方便对比（边是 (source_idx, target_idx, col_idx) 的形式，这里只对比点对）
    # 注意：all_rows 存储的是 [target, source, target, source, ...]
    def get_edges_set(rows, cols):
        edges = set()
        for i in range(0, len(rows), 2):
            target = rows[i]
            source = rows[i+1]
            edges.add((source, target))
        return edges

    edges1 = get_edges_set(rows1, cols1)
    edges2 = get_edges_set(rows2, cols2)
    
    assert count1 == count2, f"Count mismatch: {count1} vs {count2}"
    assert edges1 == edges2, "Edges content mismatch!"
    
    print("✅ Consistency test passed!")
    print(f"🚀 Speedup: {time1/time2:.2f}x")

if __name__ == "__main__":
    test_kdtree_consistency()
