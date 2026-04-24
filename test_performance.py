# -*- coding: utf-8 -*-
"""性能测试代码"""
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
optimal_allocation_linprog = main_module.optimal_allocation_linprog

# Set up logging
log_file = Path("/home/wangyb/Project/Proj_Manure/log/test_performance/test_performance.log")
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

def test_distance(distance, data, flow_data=None):
    """测试指定距离的性能"""
    logging.info(f"Testing distance: {distance}")
    start_time = time.time()
    try:
        result = optimal_allocation_linprog(data, distance, flow_data)
        elapsed_time = time.time() - start_time
        logging.info(f"Distance {distance} completed in {elapsed_time:.2f} seconds")
        return elapsed_time
    except Exception as e:
        logging.error(f"Error testing distance {distance}: {e}")
        return None

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="测试不同距离下的性能")
    parser.add_argument("--start", type=int, default=50, help="起始距离")
    parser.add_argument("--end", type=int, default=250, help="结束距离")
    parser.add_argument("--step", type=int, default=50, help="距离步长")
    parser.add_argument("--size", type=int, default=500, help="测试数据大小")
    parser.add_argument("--n_supply", type=int, default=500, help="供应点数量")
    parser.add_argument("--n_demand", type=int, default=500, help="需求点数量")
    args = parser.parse_args()

    logging.info(f"Generating test data with size={args.size}x{args.size}, n_supply={args.n_supply}, n_demand={args.n_demand}")
    data = generate_test_data((args.size, args.size), args.n_supply, args.n_demand)

    results = {}
    for distance in range(args.start, args.end + 1, args.step):
        elapsed = test_distance(distance, data)
        if elapsed is not None:
            results[distance] = elapsed

    logging.info("Test results:")
    for distance, time_taken in results.items():
        logging.info(f"Distance {distance}: {time_taken:.2f} seconds")

    # 保存结果
    import pandas as pd
    df = pd.DataFrame(list(results.items()), columns=['distance', 'time_seconds'])
    df.to_csv("/home/wangyb/Project/Proj_Manure/log/test_performance/performance_results.csv", index=False)
    logging.info("Results saved to performance_results.csv")

if __name__ == "__main__":
    main()
