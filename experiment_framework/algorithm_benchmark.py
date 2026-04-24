# -*- coding: utf-8 -*-
"""
Algorithm Comparison Framework (Experimental Version)
Evaluates five algorithm schemes using both synthetic and real-world datasets.

Target: High-quality Academic Journals (e.g., Computers and Electronics in Agriculture)
Author: AI Assistant
"""

import time
import math
import numpy as np
import pandas as pd
import rasterio as rio
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import warnings

# Correct imports from parent/sibling modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiment_framework.spatial_simulator import SpatialSimulator, DistributionType, generate_test_suite
from utils.process import process_grid_chunk, process_grid_chunk_v2
from utils.grid import get_adaptive_grid_chunks
from utils.geometry import direct_list, move_array, edges_line_func
from utils.method_selector import (
    estimate_traditional_method_time,
    estimate_adaptive_method_time,
    calculate_dynamic_threshold
)
from scipy.spatial import cKDTree


class AlgorithmType(Enum):
    TRADITIONAL = "traditional"
    DYNAMIC_GRID = "dynamic_grid"
    KD_TREE_OPTIMIZED = "kd_tree_optimized"
    HYBRID_TD = "hybrid_traditional_dynamic"
    HYBRID_TKD = "hybrid_traditional_kdtree_dynamic"


@dataclass
class ExperimentResult:
    algorithm: str
    scenario: str  # Synthetic or Real-world
    distance: int
    n_supply: int
    n_demand: int
    execution_time: float
    edges_found: int
    throughput: float


@dataclass
class ExperimentConfig:
    distances: List[int] = field(default_factory=lambda: [10, 20, 30, 40, 50, 70, 100])
    n_jobs: int = 8
    n_runs: int = 3
    warmup_runs: int = 1
    verbose: bool = True


class AlgorithmBenchmark:
    def __init__(self, config: Optional[ExperimentConfig] = None):
        self.config = config or ExperimentConfig()
        self.results: List[ExperimentResult] = []
        self.simulator = SpatialSimulator()

    def load_real_data(self, supply_path: Path, demand_path: Path) -> Tuple[np.ndarray, np.ndarray]:
        """
        Loads real-world raster data from TIF files.
        """
        with rio.open(supply_path) as dst:
            supply = dst.read(1)
            supply = np.where(supply == dst.nodata, 0, supply).astype(np.float32)
        
        with rio.open(demand_path) as dst:
            demand = dst.read(1)
            demand = np.where(demand == dst.nodata, 0, demand).astype(np.float32)
            
        return supply, demand

    def _traditional_method(self, supply_raster: np.ndarray, demand_raster: np.ndarray, distance: int, Y: int) -> Tuple[float, int]:
        start_time = time.time()
        supply_rows, supply_cols = np.nonzero(supply_raster)
        supply_set = set(zip(supply_rows.tolist(), supply_cols.tolist()))
        current_col = 0
        for dr, dc in direct_list(distance):
            moved_p = move_array(supply_raster, (dr, dc), distance)
            edges = edges_line_func(moved_p, demand_raster)
            edge_rows, edge_cols = np.nonzero(edges)
            for r, c in zip(edge_rows, edge_cols):
                source_r, source_c = r - dr, c - dc
                target_idx = r * Y + c
                if (source_r, source_c) in supply_set and 0 <= target_idx < supply_raster.size:
                    current_col += 1
        return time.time() - start_time, current_col

    def _dynamic_grid_method(self, supply_raster: np.ndarray, demand_raster: np.ndarray, distance: int, Y: int, n_jobs: int) -> Tuple[float, int]:
        X, _ = supply_raster.shape
        supply_rows, supply_cols = np.nonzero(supply_raster)
        demand_rows, demand_cols = np.nonzero(demand_raster)
        start_time = time.time()
        grid_chunks, _ = get_adaptive_grid_chunks(supply_rows, supply_cols, demand_rows, demand_cols, X, Y, distance, n_jobs)
        col_offset = 0
        for grid_bounds in grid_chunks:
            _, _, count = process_grid_chunk(grid_bounds, supply_raster, demand_raster, distance, Y)
            col_offset += count
        return time.time() - start_time, col_offset

    def _kd_tree_method(self, supply_raster: np.ndarray, demand_raster: np.ndarray, distance: int, Y: int, n_jobs: int) -> Tuple[float, int]:
        X, _ = supply_raster.shape
        supply_rows, supply_cols = np.nonzero(supply_raster)
        demand_rows, demand_cols = np.nonzero(demand_raster)
        start_time = time.time()
        grid_chunks, _ = get_adaptive_grid_chunks(supply_rows, supply_cols, demand_rows, demand_cols, X, Y, distance, n_jobs)
        col_offset = 0
        for grid_bounds in grid_chunks:
            _, _, count = process_grid_chunk_v2(grid_bounds, supply_raster, demand_raster, distance, Y)
            col_offset += count
        return time.time() - start_time, col_offset

    def run_single_experiment(self, algorithm: AlgorithmType, scenario: str, supply_raster: np.ndarray, demand_raster: np.ndarray, distance: int, n_jobs: int) -> ExperimentResult:
        Y = supply_raster.shape[1]
        n_supply = np.count_nonzero(supply_raster)
        n_demand = np.count_nonzero(demand_raster)

        if algorithm == AlgorithmType.TRADITIONAL:
            elapsed, edges = self._traditional_method(supply_raster, demand_raster, distance, Y)
        elif algorithm == AlgorithmType.DYNAMIC_GRID:
            elapsed, edges = self._dynamic_grid_method(supply_raster, demand_raster, distance, Y, n_jobs)
        elif algorithm == AlgorithmType.KD_TREE_OPTIMIZED:
            elapsed, edges = self._kd_tree_method(supply_raster, demand_raster, distance, Y, n_jobs)
        elif algorithm == AlgorithmType.HYBRID_TD:
            threshold = calculate_dynamic_threshold(n_supply, n_demand, n_jobs, supply_raster.size)
            if distance <= threshold:
                elapsed, edges = self._traditional_method(supply_raster, demand_raster, distance, Y)
            else:
                elapsed, edges = self._dynamic_grid_method(supply_raster, demand_raster, distance, Y, n_jobs)
        elif algorithm == AlgorithmType.HYBRID_TKD:
            threshold = calculate_dynamic_threshold(n_supply, n_demand, n_jobs, supply_raster.size)
            if distance <= threshold:
                elapsed, edges = self._traditional_method(supply_raster, demand_raster, distance, Y)
            else:
                elapsed, edges = self._kd_tree_method(supply_raster, demand_raster, distance, Y, n_jobs)
        
        return ExperimentResult(
            algorithm=algorithm.value,
            scenario=scenario,
            distance=distance,
            n_supply=n_supply,
            n_demand=n_demand,
            execution_time=elapsed,
            edges_found=edges,
            throughput=edges / elapsed if elapsed > 0 else 0
        )

    def run_real_world_benchmark(self, supply_path: Path, demand_path: Path):
        """
        Runs benchmark using real-world data files.
        """
        print(f"\nRunning Real-World Benchmark: {supply_path.name}")
        supply, demand = self.load_real_data(supply_path, demand_path)
        
        for algorithm in AlgorithmType:
            print(f"Testing Algorithm: {algorithm.value}")
            for d in self.config.distances:
                result = self.run_single_experiment(algorithm, "Real-World", supply, demand, d, self.config.n_jobs)
                self.results.append(result)
                print(f"  d={d}: {result.execution_time:.4f}s, edges={result.edges_found}")


if __name__ == "__main__":
    benchmark = AlgorithmBenchmark()
    
    # Example paths from 20260422.py context
    project_root = Path("/home/wangyb/Project/Proj_Manure")
    new_project_root = Path("/home/wangyb/Project/Proj_N_manure")
    resolution = 1
    
    supply_tif = new_project_root / f"data/Nsupply_demand/{resolution}km/all_supply_N_cof.tif"
    demand_tif = project_root / f"code/transport/data/Nsupply_demand/{resolution}km/Ndemand_m_prod.tif"
    
    # Only run if files exist
    if supply_tif.exists() and demand_tif.exists():
        benchmark.run_real_world_benchmark(supply_tif, demand_tif)
    else:
        print("Real-world data files not found. Please check paths.")
        # Fallback to synthetic
        supply, demand = benchmark.simulator.generate_mixed(5000, 5000)
        for d in [10, 50, 100]:
            res = benchmark.run_single_experiment(AlgorithmType.HYBRID_TKD, "Synthetic", supply, demand, d, 8)
            print(f"Synthetic d={d}: {res.execution_time:.4f}s")
