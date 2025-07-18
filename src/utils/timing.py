import functools
import time
from typing import Any, Callable


def timing_decorator(func: Callable) -> Callable:
    """
    一个简单的装饰器，用于打印函数的执行时间。
    """

    @functools.wraps(func)  # 保留原函数的元信息 (如 __name__, __doc__)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()  # 使用 perf_counter() 获得高精度计时
        result = func(*args, **kwargs)  # 执行原函数
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"方法 '{func.__name__}' 执行耗时: {elapsed_time:.4f} 秒")
        return result

    return wrapper
