"""
知乎热门话题 - 使用知乎官方 API
"""

import httpx
import news_utils

logger = news_utils.setup_logger(__name__)

API_URL = "https://api.zhihu.com/topstory/hot-list"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}


def fetch_news(limit: int = 20):
    """抓取知乎热门话题"""
    logger.info("开始抓取知乎热门话题")

    try:
        response = httpx.get(API_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        logger.warning(f"获取知乎热榜失败: {e}")
        return

    items = data.get("data", [])
    if not items:
        logger.warning("知乎热榜没有数据")
        return

    file_contents = [
        f"# 知乎热门话题 - {news_utils.current_date_formatted()}\n\n"
    ]

    for index, item in enumerate(items[:limit]):
        target = item.get("target", {})
        title = target.get("title", "无标题")
        question_id = target.get("id", "")
        answer_count = target.get("answer_count", 0)
        follower_count = target.get("follower_count", 0)
        hot_text = item.get("detail_text", "")

        # 把 API URL 转成 Web URL
        web_url = f"https://www.zhihu.com/question/{question_id}"

        file_contents.append(f"### {index + 1}. [{title}]({web_url})\n\n")
        file_contents.append(
            f"<sub>热度: {hot_text} | 回答: {answer_count} | 关注: {follower_count}</sub>\n\n"
        )
        file_contents.append("---\n\n")

    filename = get_today_news_file()
    full_content = "\n".join(file_contents)
    if news_utils.put_local_file_with_today(filename, full_content):
        logger.info(f"知乎热门话题已保存: {filename}")
    else:
        logger.error(f"无法保存知乎热门话题: {filename}")


def get_today_news_file() -> str:
    """获取今天的知乎文件名"""
    return f"zhihu_{news_utils.current_date_formatted()}.md"


def get_today_news_content() -> str:
    """获取今天的知乎内容"""
    filename = get_today_news_file()
    content = news_utils.get_local_file_with_today(filename)
    if content:
        logger.info(f"今天的知乎热门话题已存在: {filename}")
        return content

    logger.info(f"今天的知乎热门话题不存在，开始抓取: {filename}")
    fetch_news()

    content = news_utils.get_local_file_with_today(filename)
    return content or ""


if __name__ == "__main__":
    fetch_news(limit=5)
