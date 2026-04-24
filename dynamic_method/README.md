# Dynamic Method (Adaptive Grid-based Algorithm)

## 算法描述
动态自适应网格算法通过空间网格划分减少搜索空间，适合中等距离(40 < d ≤ 70)场景。

## 核心复杂度
- 时间复杂度: O(ρ_s × ρ_d × S × d²)，其中 ρ_s, ρ_d 为供需网格密度
- 空间复杂度: O(S + G)，G 为网格数量

## 核心文件
- `core.py`: 核心算法实现
- `benchmark.py`: 性能基准测试
- `test_*.py`: 单元测试

## 适用场景
- 距离 40 < d ≤ 70 km
- 稀疏供需点分布
- 中等规模数据集
