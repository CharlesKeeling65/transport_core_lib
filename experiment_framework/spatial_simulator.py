# -*- coding: utf-8 -*-
"""
空间分布模拟器
用于生成多种供需分布场景：随机聚集型、离散型、混合型

作者: AI Assistant
版本: 1.0
"""

import numpy as np
import pandas as pd
from typing import Tuple, Optional, List
from enum import Enum


class DistributionType(Enum):
    CLUSTERED = "clustered"
    DISPERSED = "dispersed"
    MIXED = "mixed"


class SpatialSimulator:
    def __init__(
        self,
        grid_size: Tuple[int, int] = (1000, 1000),
        seed: Optional[int] = None
    ):
        self.grid_size = grid_size
        if seed is not None:
            np.random.seed(seed)

    def generate_clustered(
        self,
        n_supply: int,
        n_demand: int,
        n_clusters: int = 5,
        cluster_std: float = 50.0
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        生成随机聚集型分布（多中心高斯分布）

        Args:
            n_supply: 供应点数量
            n_demand: 需求点数量
            n_clusters: 聚集中心数量
            cluster_std: 聚集标准差

        Returns:
            supply_raster: 供应点栅格数据
            demand_raster: 需求点栅格数据
        """
        X, Y = self.grid_size
        supply_raster = np.zeros((X, Y))
        demand_raster = np.zeros((X, Y))

        cluster_centers_x = np.random.randint(0, X, n_clusters)
        cluster_centers_y = np.random.randint(0, Y, n_clusters)

        for _ in range(n_supply):
            cluster_idx = np.random.randint(0, n_clusters)
            cx, cy = cluster_centers_x[cluster_idx], cluster_centers_y[cluster_idx]
            px = int(np.clip(np.random.normal(cx, cluster_std), 0, X - 1))
            py = int(np.clip(np.random.normal(cy, cluster_std), 0, Y - 1))
            supply_raster[px, py] = np.random.uniform(50, 150)

        for _ in range(n_demand):
            cluster_idx = np.random.randint(0, n_clusters)
            cx, cy = cluster_centers_x[cluster_idx], cluster_centers_y[cluster_idx]
            px = int(np.clip(np.random.normal(cx, cluster_std), 0, X - 1))
            py = int(np.clip(np.random.normal(cy, cluster_std), 0, Y - 1))
            demand_raster[px, py] = np.random.uniform(30, 120)

        return supply_raster, demand_raster

    def generate_dispersed(
        self,
        n_supply: int,
        n_demand: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        生成离散型分布（均匀随机分布）

        Args:
            n_supply: 供应点数量
            n_demand: 需求点数量

        Returns:
            supply_raster: 供应点栅格数据
            demand_raster: 需求点栅格数据
        """
        X, Y = self.grid_size
        supply_raster = np.zeros((X, Y))
        demand_raster = np.zeros((X, Y))

        supply_coords = np.random.randint(0, min(X, Y), size=(n_supply, 2))
        for coord in supply_coords:
            supply_raster[coord[0], coord[1]] = np.random.uniform(50, 150)

        demand_coords = np.random.randint(0, min(X, Y), size=(n_demand, 2))
        for coord in demand_coords:
            demand_raster[coord[0], coord[1]] = np.random.uniform(30, 120)

        return supply_raster, demand_raster

    def generate_mixed(
        self,
        n_supply: int,
        n_demand: int,
        clustered_ratio: float = 0.6
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        生成混合型分布（聚集与离散混合）

        Args:
            n_supply: 供应点数量
            n_demand: 需求点数量
            clustered_ratio: 聚集型占比 (0-1)

        Returns:
            supply_raster: 供应点栅格数据
            demand_raster: 需求点栅格数据
        """
        X, Y = self.grid_size
        supply_raster = np.zeros((X, Y))
        demand_raster = np.zeros((X, Y))

        n_supply_clustered = int(n_supply * clustered_ratio)
        n_supply_dispersed = n_supply - n_supply_clustered
        n_demand_clustered = int(n_demand * clustered_ratio)
        n_demand_dispersed = n_demand - n_demand_clustered

        if n_supply_clustered > 0:
            supply_clustered, _ = self.generate_clustered(
                n_supply_clustered, 0, n_clusters=3
            )
            supply_raster += supply_clustered

        if n_supply_dispersed > 0:
            supply_dispersed, _ = self.generate_dispersed(
                n_supply_dispersed, 0
            )
            supply_raster += supply_dispersed

        if n_demand_clustered > 0:
            _, demand_clustered = self.generate_clustered(
                0, n_demand_clustered, n_clusters=3
            )
            demand_raster += demand_clustered

        if n_demand_dispersed > 0:
            _, demand_dispersed = self.generate_dispersed(
                0, n_demand_dispersed
            )
            demand_raster += demand_dispersed

        return supply_raster, demand_raster

    def generate_from_type(
        self,
        distribution_type: DistributionType,
        n_supply: int,
        n_demand: int,
        **kwargs
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        根据类型生成对应分布

        Args:
            distribution_type: 分布类型
            n_supply: 供应点数量
            n_demand: 需求点数量
            **kwargs: 其他参数

        Returns:
            supply_raster: 供应点栅格数据
            demand_raster: 需求点栅格数据
        """
        if distribution_type == DistributionType.CLUSTERED:
            return self.generate_clustered(n_supply, n_demand, **kwargs)
        elif distribution_type == DistributionType.DISPERSED:
            return self.generate_dispersed(n_supply, n_demand)
        elif distribution_type == DistributionType.MIXED:
            return self.generate_mixed(n_supply, n_demand, **kwargs)
        else:
            raise ValueError(f"Unknown distribution type: {distribution_type}")

    def save_as_csv(
        self,
        supply_raster: np.ndarray,
        demand_raster: np.ndarray,
        output_path: str
    ):
        """
        保存为CSV格式（稀疏表示）

        Args:
            supply_raster: 供应点栅格数据
            demand_raster: 需求点栅格数据
            output_path: 输出路径
        """
        X, Y = supply_raster.shape

        supply_rows, supply_cols = np.nonzero(supply_raster)
        demand_rows, demand_cols = np.nonzero(demand_raster)

        supply_df = pd.DataFrame({
            'x': supply_rows,
            'y': supply_cols,
            'value': supply_raster[supply_rows, supply_cols]
        })

        demand_df = pd.DataFrame({
            'x': demand_rows,
            'y': demand_cols,
            'value': demand_raster[demand_rows, demand_cols]
        })

        with pd.ExcelWriter(output_path) as writer:
            supply_df.to_excel(writer, sheet_name='Supply', index=False)
            demand_df.to_excel(writer, sheet_name='Demand', index=False)


def generate_test_suite() -> List[dict]:
    """
    生成标准化测试用例库

    Returns:
        测试用例列表
    """
    test_cases = []

    test_cases.append({
        'name': '小规模均匀分布',
        'n_supply': 1000,
        'n_demand': 1000,
        'grid_size': (500, 500),
        'distribution': DistributionType.DISPERSED,
        'expected_density': 'low'
    })

    test_cases.append({
        'name': '中规模聚集分布',
        'n_supply': 5000,
        'n_demand': 5000,
        'grid_size': (1000, 1000),
        'distribution': DistributionType.CLUSTERED,
        'n_clusters': 8,
        'expected_density': 'medium'
    })

    test_cases.append({
        'name': '大规模混合分布',
        'n_supply': 10000,
        'n_demand': 10000,
        'grid_size': (2000, 2000),
        'distribution': DistributionType.MIXED,
        'clustered_ratio': 0.7,
        'expected_density': 'high'
    })

    test_cases.append({
        'name': '极端稀疏场景',
        'n_supply': 500,
        'n_demand': 800,
        'grid_size': (5000, 5000),
        'distribution': DistributionType.DISPERSED,
        'expected_density': 'very_low'
    })

    test_cases.append({
        'name': '极端稠密场景',
        'n_supply': 20000,
        'n_demand': 20000,
        'grid_size': (500, 500),
        'distribution': DistributionType.CLUSTERED,
        'n_clusters': 10,
        'expected_density': 'very_high'
    })

    return test_cases


if __name__ == "__main__":
    simulator = SpatialSimulator(grid_size=(1000, 1000), seed=42)

    print("=== 空间分布模拟器测试 ===")

    print("\n1. 生成聚集型分布...")
    supply_c, demand_c = simulator.generate_from_type(
        DistributionType.CLUSTERED, 5000, 5000, n_clusters=5
    )
    print(f"   供应点数量: {np.count_nonzero(supply_c)}")
    print(f"   需求点数量: {np.count_nonzero(demand_c)}")

    print("\n2. 生成离散型分布...")
    supply_d, demand_d = simulator.generate_from_type(
        DistributionType.DISPERSED, 5000, 5000
    )
    print(f"   供应点数量: {np.count_nonzero(supply_d)}")
    print(f"   需求点数量: {np.count_nonzero(demand_d)}")

    print("\n3. 生成混合型分布...")
    supply_m, demand_m = simulator.generate_from_type(
        DistributionType.MIXED, 5000, 5000, clustered_ratio=0.6
    )
    print(f"   供应点数量: {np.count_nonzero(supply_m)}")
    print(f"   需求点数量: {np.count_nonzero(demand_m)}")

    print("\n4. 测试用例库:")
    test_suite = generate_test_suite()
    for i, case in enumerate(test_suite):
        print(f"   [{i+1}] {case['name']}: n={case['n_supply']}, density={case['expected_density']}")

    print("\n=== 测试完成 ===")
