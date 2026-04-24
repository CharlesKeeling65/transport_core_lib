# -*- coding: utf-8 -*-
"""
实验结果可视化模块
生成算法收敛曲线、解空间分布图、性能热力图等分析图表

作者: AI Assistant
版本: 1.0
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
from typing import Optional, List, Tuple, Dict
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['figure.dpi'] = 150


class ResultVisualizer:
    def __init__(
        self,
        style: str = 'seaborn-v0_8-whitegrid',
        output_dir: str = './visualization_output'
    ):
        self.style = style
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        sns.set_style(style)

    def plot_convergence_curve(
        self,
        df: pd.DataFrame,
        x_col: str = 'distance',
        y_col: str = 'execution_time',
        hue_col: str = 'algorithm',
        title: str = 'Algorithm Convergence Curve',
        xlabel: str = 'Distance (km)',
        ylabel: str = 'Execution Time (s)',
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        绘制算法收敛曲线
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        for algorithm in df[hue_col].unique():
            algo_data = df[df[hue_col] == algorithm]
            ax.plot(
                algo_data[x_col],
                algo_data[y_col],
                marker='o',
                label=algorithm,
                linewidth=2,
                markersize=6
            )

        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(title='Algorithm', fontsize=10)
        ax.grid(True, alpha=0.3)

        if save_path:
            fig.savefig(self.output_dir / save_path, bbox_inches='tight')
            print(f"收敛曲线已保存: {self.output_dir / save_path}")

        return fig

    def plot_speedup_comparison(
        self,
        df: pd.DataFrame,
        x_col: str = 'distance',
        y_col: str = 'speedup',
        title: str = 'KD-Tree Speedup Ratio',
        xlabel: str = 'Distance (km)',
        ylabel: str = 'Speedup (×)',
        baseline: float = 1.0,
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        绘制加速比对比图
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        ax.plot(df[x_col], df[y_col], marker='s', color='green', linewidth=2, markersize=8)
        ax.axhline(y=baseline, color='red', linestyle='--', linewidth=1.5, label=f'Baseline (×{baseline})')

        ax.fill_between(df[x_col], baseline, df[y_col], alpha=0.3, color='green')

        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        if save_path:
            fig.savefig(self.output_dir / save_path, bbox_inches='tight')
            print(f"加速比图已保存: {self.output_dir / save_path}")

        return fig

    def plot_performance_heatmap(
        self,
        df: pd.DataFrame,
        value_col: str = 'execution_time',
        index_col: str = 'distance',
        columns_col: str = 'algorithm',
        title: str = 'Performance Heatmap',
        cmap: str = 'YlOrRd',
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        绘制性能热力图
        """
        pivot_df = df.pivot_table(
            values=value_col,
            index=index_col,
            columns=columns_col,
            aggfunc='mean'
        )

        fig, ax = plt.subplots(figsize=(14, 8))

        sns.heatmap(
            pivot_df,
            annot=True,
            fmt='.3f',
            cmap=cmap,
            ax=ax,
            cbar_kws={'label': value_col}
        )

        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Algorithm', fontsize=12)
        ax.set_ylabel(index_col, fontsize=12)

        if save_path:
            fig.savefig(self.output_dir / save_path, bbox_inches='tight')
            print(f"热力图已保存: {self.output_dir / save_path}")

        return fig

    def plot_throughput_comparison(
        self,
        df: pd.DataFrame,
        x_col: str = 'distance',
        y_col: str = 'throughput',
        hue_col: str = 'algorithm',
        title: str = 'Algorithm Throughput Comparison',
        xlabel: str = 'Distance (km)',
        ylabel: str = 'Throughput (edges/s)',
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        绘制吞吐量对比图
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        for algorithm in df[hue_col].unique():
            algo_data = df[df[hue_col] == algorithm].sort_values(x_col)
            ax.plot(
                algo_data[x_col],
                algo_data[y_col],
                marker='o',
                label=algorithm,
                linewidth=2
            )

        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(title='Algorithm', fontsize=10)
        ax.grid(True, alpha=0.3)

        if save_path:
            fig.savefig(self.output_dir / save_path, bbox_inches='tight')
            print(f"吞吐量图已保存: {self.output_dir / save_path}")

        return fig

    def plot_spatial_distribution(
        self,
        supply_coords: np.ndarray,
        demand_coords: np.ndarray,
        title: str = 'Supply-Demand Spatial Distribution',
        supply_label: str = 'Supply',
        demand_label: str = 'Demand',
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        绘制供需空间分布图
        """
        fig, ax = plt.subplots(figsize=(10, 10))

        if len(supply_coords) > 0:
            ax.scatter(
                supply_coords[:, 1],
                supply_coords[:, 0],
                c='green',
                s=20,
                alpha=0.6,
                label=supply_label,
                marker='o'
            )

        if len(demand_coords) > 0:
            ax.scatter(
                demand_coords[:, 1],
                demand_coords[:, 0],
                c='red',
                s=20,
                alpha=0.6,
                label=demand_label,
                marker='^'
            )

        ax.set_xlabel('Column', fontsize=12)
        ax.set_ylabel('Row', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')

        if save_path:
            fig.savefig(self.output_dir / save_path, bbox_inches='tight')
            print(f"空间分布图已保存: {self.output_dir / save_path}")

        return fig

    def plot_complexity_analysis(
        self,
        time_complexity: Dict[str, callable],
        n_range: np.ndarray,
        d: int = 50,
        title: str = 'Time Complexity Analysis',
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        绘制理论复杂度对比图
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        colors = ['blue', 'orange', 'green', 'red', 'purple']
        for (name, func), color in zip(time_complexity.items(), colors):
            ax.plot(n_range, func(n_range, d), label=name, color=color, linewidth=2)

        ax.set_xlabel('Data Size N', fontsize=12)
        ax.set_ylabel('Time Complexity T(N, d)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log')
        ax.set_yscale('log')

        if save_path:
            fig.savefig(self.output_dir / save_path, bbox_inches='tight')
            print(f"复杂度分析图已保存: {self.output_dir / save_path}")

        return fig

    def plot_algorithm_comparison_bar(
        self,
        df: pd.DataFrame,
        x_col: str = 'algorithm',
        y_col: str = 'execution_time',
        hue_col: Optional[str] = None,
        title: str = 'Algorithm Execution Time Comparison',
        xlabel: str = 'Algorithm',
        ylabel: str = 'Execution Time (s)',
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        绘制算法对比柱状图
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        if hue_col:
            sns.barplot(data=df, x=x_col, y=y_col, hue=hue_col, ax=ax, ci='sd')
        else:
            sns.barplot(data=df, x=x_col, y=y_col, ax=ax, ci='sd', color='steelblue')

        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3, axis='y')

        if save_path:
            fig.savefig(self.output_dir / save_path, bbox_inches='tight')
            print(f"柱状图已保存: {self.output_dir / save_path}")

        return fig

    def create_dashboard(
        self,
        results_df: pd.DataFrame,
        output_prefix: str = 'dashboard'
    ) -> Dict[str, plt.Figure]:
        """
        创建综合仪表板
        """
        dashboards = {}

        dashboards['convergence'] = self.plot_convergence_curve(
            results_df,
            title='Convergence Curves by Algorithm',
            save_path=f'{output_prefix}_convergence.png'
        )

        dashboards['heatmap'] = self.plot_performance_heatmap(
            results_df,
            title='Performance Heatmap (Execution Time)',
            save_path=f'{output_prefix}_heatmap.png'
        )

        dashboards['throughput'] = self.plot_throughput_comparison(
            results_df,
            title='Throughput Comparison',
            save_path=f'{output_prefix}_throughput.png'
        )

        dashboards['bar'] = self.plot_algorithm_comparison_bar(
            results_df,
            title='Average Execution Time by Algorithm',
            hue_col='distance',
            save_path=f'{output_prefix}_bar.png'
        )

        plt.close('all')

        return dashboards


def generate_sample_visualization(output_dir: str = './visualization_output'):
    """
    生成示例可视化图表
    """
    visualizer = ResultVisualizer(output_dir=output_dir)

    np.random.seed(42)
    sample_data = []
    for algo in ['traditional', 'dynamic_grid', 'kd_tree_optimized', 'hybrid_td', 'hybrid_tkd']:
        for d in [10, 20, 30, 40, 50, 70, 100]:
            for _ in range(3):
                base_time = d * 0.01 if algo != 'kd_tree_optimized' else d * 0.003
                sample_data.append({
                    'algorithm': algo,
                    'distance': d,
                    'execution_time': base_time + np.random.uniform(0, 0.5),
                    'edges_found': int(1000 * d / 10 + np.random.uniform(-100, 100)),
                    'throughput': 1000 + np.random.uniform(-50, 50)
                })

    df = pd.DataFrame(sample_data)

    print("1. 生成收敛曲线...")
    visualizer.plot_convergence_curve(df, save_path='convergence_curve.png')

    print("2. 生成性能热力图...")
    visualizer.plot_performance_heatmap(df, save_path='performance_heatmap.png')

    print("3. 生成吞吐量对比图...")
    visualizer.plot_throughput_comparison(df, save_path='throughput.png')

    print("4. 生成复杂度分析图...")
    complexity_functions = {
        'Traditional O(d×S)': lambda n, d: d * n * 0.001,
        'Dynamic O(ρd²)': lambda n, d: n * (d**2) * 0.0001,
        'KD-Tree O(NlogN)': lambda n, d: n * np.log2(n) * 0.001
    }
    n_range = np.logspace(2, 5, 50)
    visualizer.plot_complexity_analysis(complexity_functions, n_range, d=50, save_path='complexity.png')

    print(f"\n所有可视化图表已保存至: {output_dir}")
    return df


if __name__ == "__main__":
    print("=== 实验结果可视化模块测试 ===\n")

    df = generate_sample_visualization()

    print("\n=== 测试完成 ===")
