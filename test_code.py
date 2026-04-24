import time
import numpy as np

# import matplotlib.pyplot as plt
from functools import wraps, lru_cache
import math

# 用于存储测试结果
results = {"original": [], "optimized": [], "distances": []}


def timeit(func):
    """计时器装饰器，用于测量函数执行时间"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, end_time - start_time

    return wrapper


def generate_test_raster(size=100):
    """生成测试用的栅格数据"""
    return np.random.rand(size, size)


def get_unit_directions():
    """生成所有单位方向"""
    unit_directions = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            unit_directions.append((dr, dc))
    return unit_directions


def decompose_direction(dr, dc):
    """将方向分解为单位方向序列"""
    steps = []
    min_abs = min(abs(dr), abs(dc))
    d_sign_r = 1 if dr >= 0 else -1
    d_sign_c = 1 if dc >= 0 else -1

    for _ in range(min_abs):
        steps.append((d_sign_r, d_sign_c))

    remaining_r = abs(dr) - min_abs
    remaining_c = abs(dc) - min_abs

    for _ in range(remaining_r):
        steps.append((d_sign_r, 0))

    for _ in range(remaining_c):
        steps.append((0, d_sign_c))

    return steps


@timeit
def original_shift_method(raster, distance):
    """使用原始方法计算所有方向的平移（只pad一次，每方向直接roll）"""
    directions = direct_list_original(distance)
    shifted_arrays = {}
    max_distance = distance
    padded_raster = np.pad(raster, max_distance, mode="constant").astype(np.float32)
    for dr, dc in directions:
        shifted_padded = np.roll(padded_raster, (dr, dc), axis=(0, 1))
        shifted = shifted_padded[max_distance:-max_distance, max_distance:-max_distance]
        shifted_arrays[(dr, dc)] = shifted
    return shifted_arrays


@timeit
def per_direction_pad_method(raster, distance):
    """每个方向都单独pad+roll"""
    directions = direct_list_original(distance)
    shifted_arrays = {}
    for dr, dc in directions:
        shifted = move_array(raster, (dr, dc), distance)
        shifted_arrays[(dr, dc)] = shifted
    return shifted_arrays


@timeit
def pad_once_method(raster, distance):
    """pad一次，每方向直接roll"""
    directions = direct_list_original(distance)
    shifted_arrays = {}
    max_distance = distance
    padded_raster = np.pad(raster, max_distance, mode="constant").astype(np.float32)
    for dr, dc in directions:
        shifted_padded = np.roll(padded_raster, (dr, dc), axis=(0, 1))
        shifted = shifted_padded[max_distance:-max_distance, max_distance:-max_distance]
        shifted_arrays[(dr, dc)] = shifted
    return shifted_arrays


def compare_performance(max_distance=10, raster_size=100, runs_per_distance=3):
    """比较两种实现的性能"""
    raster = generate_test_raster(raster_size)
    for d in range(1, max_distance + 1):
        print(f"Testing distance {d}...")
        per_pad_times = []
        pad_once_times = []
        for _ in range(runs_per_distance):
            _, t1 = per_direction_pad_method(raster, d)
            per_pad_times.append(t1)
            _, t2 = pad_once_method(raster, d)
            pad_once_times.append(t2)
        avg_per_pad = sum(per_pad_times) / runs_per_distance
        avg_pad_once = sum(pad_once_times) / runs_per_distance
        speedup = avg_per_pad / avg_pad_once if avg_pad_once > 0 else float("inf")
        results["distances"].append(d)
        results["original"].append(avg_per_pad)
        results["optimized"].append(avg_pad_once)
        print(
            f"  Distance {d}: Per-direction pad={avg_per_pad:.4f}s, Pad-once={avg_pad_once:.4f}s, Speedup={speedup:.2f}x"
        )
    return results


# def plot_results():
#     """绘制性能比较结果"""
#     plt.figure(figsize=(14, 10))

#     # 绘制执行时间对比图
#     plt.subplot(2, 1, 1)
#     plt.plot(results['distances'], results['original'], 'o-', label='Original Method')
#     plt.plot(results['distances'], results['optimized'], 's-', label='Optimized Method')
#     plt.xlabel('Distance')
#     plt.ylabel('Execution Time (seconds)')
#     plt.title('Performance Comparison: Original vs Optimized Shift Method')
#     plt.grid(True)
#     plt.legend()

#     # 绘制加速比图
#     plt.subplot(2, 1, 2)
#     speedups = [orig/opt for orig, opt in zip(results['original'], results['optimized'])]
#     plt.plot(results['distances'], speedups, 'g^-')
#     plt.xlabel('Distance')
#     plt.ylabel('Speedup Factor (Original/Optimized)')
#     plt.title('Speedup Factor by Distance')
#     plt.grid(True)
#     plt.axhline(y=1, color='r', linestyle='--', label='No Improvement')
#     plt.legend()

#     plt.tight_layout()
#     plt.savefig('shift_performance_comparison.png')
#     plt.show()


# 原始方法实现
def direct_list_original(distance):
    """原代码中的direct_list函数"""
    sqrt_2_div_2 = math.sqrt(2) / 2
    max_square_value = (distance + sqrt_2_div_2) ** 2
    min_square_value = (distance - 1 + sqrt_2_div_2) ** 2
    directions = []
    for dr in range(-distance, distance + 1):
        max_square = max_square_value - dr**2
        min_square = min_square_value - dr**2
        dc_max = int(np.sqrt(max_square))
        if min_square < 0:
            dc_min = 0
            for dc in range(-dc_max, dc_max + 1):
                directions.append((dr, dc))
        else:
            dc_min = int(math.ceil(math.sqrt(min_square)))
            for dc in list(range(-dc_max, -dc_min + 1)) + list(
                range(dc_min, dc_max + 1)
            ):
                directions.append((dr, dc))
    return directions


def direct_list_optimized(distance):
    """优化后的direct_list函数"""
    if distance == 1:
        return direct_list_original(1)
    else:
        prev_directions = set(direct_list_optimized(distance - 1))
        current_directions = []
        for dr, dc in direct_list_original(distance):
            if (dr, dc) not in prev_directions:
                current_directions.append((dr, dc))
        return current_directions


def move_array(arr, direct, max_distance):
    """原代码中的move_array函数"""
    di, dj = direct
    padded_arr = np.pad(arr, max_distance, mode="constant").astype(np.float32)
    moved_arr = np.roll(padded_arr, (di, dj), axis=(0, 1)).astype(np.float32)
    return moved_arr[max_distance:-max_distance, max_distance:-max_distance]


# 运行测试
if __name__ == "__main__":
    # 调整这些参数以测试不同场景
    MAX_DISTANCE = 50  # 测试的最大距离
    RASTER_SIZE = 1000  # 测试栅格的大小
    RUNS_PER_DISTANCE = 3  # 每个距离运行的次数，取平均值

    print(
        f"Starting performance test with raster size {RASTER_SIZE}x{RASTER_SIZE} up to distance {MAX_DISTANCE}"
    )
    results = compare_performance(
        max_distance=MAX_DISTANCE,
        raster_size=RASTER_SIZE,
        runs_per_distance=RUNS_PER_DISTANCE,
    )

    # 输出汇总结果
    total_orig_time = sum(results["original"])
    total_opt_time = sum(results["optimized"])
    overall_speedup = total_orig_time / total_opt_time

    print("\n=== Summary ===")
    print(f"Total original time: {total_orig_time:.4f}s")
    print(f"Total optimized time: {total_opt_time:.4f}s")
    print(f"Overall speedup: {overall_speedup:.2f}x")
    print(f"Performance comparison chart saved as 'shift_performance_comparison.png'")
