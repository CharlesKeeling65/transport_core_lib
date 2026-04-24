# -*- coding: utf-8 -*-
"""测试高密度数据的动态分界点"""
import time
import numpy as np
import logging
from pathlib import Path
import argparse

import importlib.util
import sys

# 导入主模块
spec = importlib.util.spec_from_file_location("main_module", "final_optimal_transport_by_organic_1km+liquid-N-1011.py")
main_module = importlib.util.module_from_spec(spec)
sys.modules["main_module"] = main_module
spec.loader.exec_module(main_module)
vectorized_edges = main_module.vectorized_edges

# Set up logging
log_file = Path("/home/wangyb/Project/Proj_Manure/log/test_performance/test_high_density.log")
log_file.parent.mkdir(exist_ok=True, parents=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)

def generate_high_density_data(size=(200, 200), density=0.5):
    """生成高密度测试数据"""
    data = np.zeros(size, dtype=np.float32)
    total_pixels = size[0] * size[1]
    n_points = int(total_pixels * density)
    
    # 随机生成供应点和需求点
    indices = np.random.choice(total_pixels, n_points, replace=False)
    rows = indices // size[1]
    cols = indices % size[1]
    
    # 一半作为供应点，一半作为需求点
    n_supply = n_points // 2
    n_demand = n_points - n_supply
    
    data[rows[:n_supply], cols[:n_supply]] = np.random.uniform(1, 10, n_supply)
    data[rows[n_supply:], cols[n_supply:]] = -np.random.uniform(1, 10, n_demand)
    
    return data, n_supply, n_demand

def test_vectorized_edges(distance, data):
    """测试vectorized_edges函数的性能"""
    logging.info(f"Testing vectorized_edges for distance: {distance}")
    start_time = time.time()
    p_raster = np.where(data > 0, data, 0)
    n_raster = np.where(data < 0, data, 0)
    Y = data.shape[1]
    try:
        A, rows, cols = vectorized_edges(p_raster, n_raster, distance, Y)
        elapsed_time = time.time() - start_time
        logging.info(f"Distance {distance} completed in {elapsed_time:.2f} seconds")
        logging.info(f"A shape: {A.shape}, nnz: {A.nnz}")
        return elapsed_time, A.shape, A.nnz
    except Exception as e:
        logging.error(f"Error testing distance {distance}: {e}")
        return None, None, None

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="测试高密度数据的动态分界点")
    parser.add_argument("--density", type=float, default=0.5, help="数据密度")
    parser.add_argument("--size", type=int, default=200, help="测试数据大小")
    args = parser.parse_args()

    logging.info(f"Generating high density test data with size={args.size}x{args.size}, density={args.density}")
    data, n_supply, n_demand = generate_high_density_data((args.size, args.size), args.density)
    logging.info(f"Generated data with {n_supply} supply points and {n_demand} demand points")

    # 测试不同距离
    distances = [50, 100, 150]
    results = {}
    for distance in distances:
        elapsed, shape, nnz = test_vectorized_edges(distance, data)
        if elapsed is not None:
            results[distance] = {
                'time_seconds': elapsed,
                'matrix_shape': shape,
                'non_zero_count': nnz
            }

    logging.info("Test results:")
    for distance, info in results.items():
        logging.info(f"Distance {distance}: {info['time_seconds']:.2f}s, Shape: {info['matrix_shape']}, NNZ: {info['non_zero_count']}")

if __name__ == "__main__":
    main()
