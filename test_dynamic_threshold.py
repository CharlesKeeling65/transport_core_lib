# -*- coding: utf-8 -*-
"""测试动态分界点性能"""
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
log_file = Path("/home/wangyb/Project/Proj_Manure/log/test_performance/test_dynamic_threshold.log")
log_file.parent.mkdir(exist_ok=True, parents=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)

def generate_test_data(size=(1000, 1000), n_supply=1000, n_demand=1000):
    """生成测试数据"""
    data = np.zeros(size, dtype=np.float32)
    # 随机生成供应点
    supply_rows = np.random.randint(0, size[0], n_supply)
    supply_cols = np.random.randint(0, size[1], n_supply)
    data[supply_rows, supply_cols] = np.random.uniform(1, 10, n_supply)
    # 随机生成需求点
    demand_rows = np.random.randint(0, size[0], n_demand)
    demand_cols = np.random.randint(0, size[1], n_demand)
    data[demand_rows, demand_cols] = -np.random.uniform(1, 10, n_demand)
    return data

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
    parser = argparse.ArgumentParser(description="测试动态分界点性能")
    parser.add_argument("--start", type=int, default=50, help="起始距离")
    parser.add_argument("--end", type=int, default=250, help="结束距离")
    parser.add_argument("--step", type=int, default=25, help="距离步长")
    parser.add_argument("--size", type=int, default=300, help="测试数据大小")
    parser.add_argument("--n_supply", type=int, default=300, help="供应点数量")
    parser.add_argument("--n_demand", type=int, default=300, help="需求点数量")
    args = parser.parse_args()

    logging.info(f"Generating test data with size={args.size}x{args.size}, n_supply={args.n_supply}, n_demand={args.n_demand}")
    data = generate_test_data((args.size, args.size), args.n_supply, args.n_demand)

    results = {}
    for distance in range(args.start, args.end + 1, args.step):
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

    # 保存结果
    import pandas as pd
    df = pd.DataFrame.from_dict(results, orient='index')
    df.index.name = 'distance'
    df.to_csv("/home/wangyb/Project/Proj_Manure/log/test_performance/dynamic_threshold_results.csv")
    logging.info("Results saved to dynamic_threshold_results.csv")

if __name__ == "__main__":
    main()
