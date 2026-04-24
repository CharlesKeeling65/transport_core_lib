# KD-Tree Optimized Dynamic Method

## 算法描述
基于 KD-Tree 空间索引优化的自适应网格算法，通过半径查询替代暴力比对，适合大距离(d > 70)场景。

## 核心复杂度
- 时间复杂度: O(N log N)，其中 N 为总点数
- 空间复杂度: O(N)

## 核心文件
- `core.py`: 核心算法实现 (基于 scipy.spatial.cKDTree)
- `benchmark.py`: 性能基准测试
- `test_*.py`: 单元测试

## 适用场景
- 距离 d > 70 km
- 大规模空间数据
- 高效并行计算

## 性能提升
相比原始动态方法，提升约 3-5 倍。
