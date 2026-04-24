# Traditional Method (Pixel-based Translation Algorithm)

## 算法描述
传统像素平移算法通过直接移动像素位置并使用位运算检测供需匹配，适合小距离(d≤40)场景。

## 核心复杂度
- 时间复杂度: O(d × S)，其中 d 为距离，S 为像素总数
- 空间复杂度: O(S)

## 核心文件
- `core.py`: 核心算法实现
- `benchmark.py`: 性能基准测试
- `test_*.py`: 单元测试

## 适用场景
- 距离 d ≤ 40 km
- 高密度供需点分布
- 小规模数据集
