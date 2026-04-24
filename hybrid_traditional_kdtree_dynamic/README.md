# Hybrid: Traditional + KD-Tree Optimized Method

## 算法描述
两阶段混合算法策略：距离 d ≤ T₁ 时使用传统像素平移方法，d > T₁ 时使用 KD-Tree 空间索引优化方法。

## 核心复杂度
- 切换阈值 T₁ 由 `calculate_dynamic_threshold` 动态确定
- 时间复杂度: min(O(d × S), O(N log N))

## 核心文件
- `selector.py`: 两阶段算法切换选择器
- `benchmark.py`: 性能基准测试
- `test_*.py`: 单元测试

## 适用场景
- 大规模数据处理
- 全距离范围优化
- 追求最佳性能表现
