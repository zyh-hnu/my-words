"""
可以把 LLM 接口换成 Github Copilot 接口.
如果不行就使用 llama-cpp-python + Yi-1.5-6B 的本地模型
"""

import atexit
import time
from typing import Optional

from openai import OpenAI, APIError, APIConnectionError, RateLimitError
from openai._exceptions import InternalServerError

import config
import news_utils
import tokenizer

logger = news_utils.setup_logger(__name__)

_MAX_RETRIES = 3
_BASE_DELAY = 2.0


# 全局统计变量
class LLMStats:
    def __init__(self):
        self.total_calls = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.total_time = 0.0
        self.input_cost_per_million_tokens = 2.0  # DeepSeek: 2元人民币/百万token
        self.output_cost_per_million_tokens = 8.0  # DeepSeek: 8元人民币/百万token

    def add_call(self, input_msg: str, output_msg: str, duration: float):
        input_tokens = tokenizer.calculate_tokenizer(input_msg)
        output_tokens = tokenizer.calculate_tokenizer(output_msg)
        self.total_tokens += input_tokens + output_tokens
        self.total_calls += 1
        self.total_cost += (input_tokens / 1_000_000) * self.input_cost_per_million_tokens
        self.total_cost += (output_tokens / 1_000_000) * self.output_cost_per_million_tokens
        self.total_time += duration

    def get_summary(self) -> str:
        avg_time = self.total_time / self.total_calls if self.total_calls > 0 else 0
        return (
            f"LLM统计汇总 - 总调用次数: {self.total_calls}, "
            f"总Token: {self.total_tokens:,}, "
            f"总费用: ¥{self.total_cost:.6f}, "
            f"总耗时: {self.total_time:.2f}s, "
            f"平均耗时: {avg_time:.2f}s/次"
        )


llm_stats = LLMStats()


def _print_llm_stats_on_exit():
    """进程退出时打印LLM统计信息"""
    if llm_stats.total_calls > 0:
        print(f"\n[进程退出] {llm_stats.get_summary()}")


# 注册退出处理函数
atexit.register(_print_llm_stats_on_exit)


def get_llm_stats() -> str:
    """获取LLM使用统计信息"""
    return llm_stats.get_summary()


def _build_client() -> OpenAI:
    """构建 OpenAI 客户端（复用连接池）"""
    return OpenAI(
        api_key=config.settings.openai_api_key,
        base_url=config.settings.openai_base_url,
        timeout=60.0,
        max_retries=0,  # 自定义重试逻辑
    )


def _should_retry(exception: Exception) -> bool:
    """判断错误是否值得重试"""
    return isinstance(exception, (APIConnectionError, RateLimitError, InternalServerError))


def _call_llm(system_prompt: str, user_prompt: str) -> str:
    """调用 LLM，带重试机制"""
    client = _build_client()
    model = config.settings.llm_model

    last_exception = None
    for attempt in range(_MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=3000,
            )
        except Exception as e:
            last_exception = e
            if attempt < _MAX_RETRIES and _should_retry(e):
                delay = _BASE_DELAY * (2 ** attempt)
                logger.warning(f"LLM 请求失败 (第{attempt + 1}次)，{delay:.0f}s 后重试: {type(e).__name__}: {e}")
                time.sleep(delay)
                continue
            raise  # 最后一次失败或不可重试的错误直接抛出

        result = response.choices[0].message.content
        if result is None:
            raise ValueError("LLM 返回内容为空")
        return result.strip()

    # 理论上不会执行到这里，但保留兜底
    raise last_exception  # type: ignore


def one_shoot(system_prompt: str, user_prompt: str) -> Optional[str]:
    """
    使用LLM对内容进行总结

    Args:
        system_prompt (str): 系统提示
        user_prompt (str): 用户提示

    Returns:
        Optional[str]: 总结后的内容，失败则返回None
    """
    start_time = time.time()

    try:
        result = _call_llm(system_prompt, user_prompt)
        duration = time.time() - start_time

        llm_stats.add_call(
            input_msg=system_prompt + user_prompt,
            output_msg=result,
            duration=duration,
        )

        logger.info(f"LLM 调用成功 (模型: {config.settings.llm_model}, 耗时: {duration:.2f}s)")
        return result

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"LLM 调用失败 ({config.settings.llm_model}, 耗时: {duration:.2f}s): {type(e).__name__}: {e}")
        return None


def concurrent_one_shoot(prompts: list[tuple[str, str]]) -> list[Optional[str]]:
    """
    并发处理多个LLM请求

    Args:
        prompts (list[tuple[str, str]]): 包含多个 (system_prompt, user_prompt) 的列表

    Returns:
        list[Optional[str]]: 每个请求的结果列表
    """
    from concurrent.futures import ThreadPoolExecutor

    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(one_shoot, system, user) for system, user in prompts]
        for future in futures:
            results.append(future.result())

    return results


if __name__ == "__main__":
    res = one_shoot("你好", "你好")
    print(res)
    print(get_llm_stats())