# Hybrid: Traditional + Dynamic Method

## 算法描述
混合算法策略：距离 d ≤ T 时使用传统方法，d > T 时使用动态网格方法。

## 核心复杂度
- 切换阈值 T 由 `calculate_dynamic_threshold` 动态确定
- 时间复杂度: min(O(d × S), O(ρ_s × ρ_d × S × d²))

## 核心文件
- `selector.py`: 算法切换选择器
- `benchmark.py`: 性能基准测试
- `test_*.py`: 单元测试

## 适用场景
- 自适应选择最优算法
- 平衡计算效率与精度
- 通用场景推荐
