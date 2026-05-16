"""AI News RSS 源 - https://news.smol.ai/rss.xml"""

from datetime import datetime

import news_utils

logger = news_utils.setup_logger(__name__)

RSS_URL = "https://news.smol.ai/rss.xml"


def fetch_news():
    """抓取 AI News 最新内容"""
    logger.info("开始抓取 AINews 最新内容")
    
    # 获取最新 RSS 条目
    entries = news_utils.get_rss_entries(RSS_URL, limit=1)
    if not entries:
        logger.error("没有获取到 AI News RSS 条目")
        return

    entry = entries[0]
    link = entry.get("link", "")
    title = entry.get("title", "无标题")
    summary = entry.get("summary", "")
    
    # 转换 HTML 摘要为 Markdown
    if summary:
        summary = news_utils.convert_html_to_markdown(summary)

    current_date = datetime.now().strftime("%Y-%m-%d")

    # 构建内容
    content = f"# AINews - {current_date}\n\n"
    content += f"> [原文链接]({link})\n\n"
    content += f"## {title}\n\n"
    
    if summary:
        content += f"{summary}\n\n"

    # 保存到文件
    filename = get_today_news_file()
    if news_utils.put_local_file_with_today(filename, content):
        logger.info(f"✓ AI News 已保存: {filename}")
    else:
        logger.error(f"✗ 无法保存 AI News: {filename}")


def get_today_news_file():
    """获取今天的 AI News 文件名"""
    return f"ai_news_{news_utils.current_date_formatted()}.md"


def get_today_news_content() -> str:
    """获取今天的 AI News 内容"""
    filename = get_today_news_file()
    content = news_utils.get_local_file_with_today(filename)
    if content:
        logger.info(f"今天的 AI News 已存在: {filename}")
        return content

    logger.info(f"今天的 AI News 不存在，开始抓取: {filename}")
    fetch_news()

    content = news_utils.get_local_file_with_today(filename)
    return content or ""


if __name__ == "__main__":
    fetch_news()