"""
36氪 RSS 源 - https://36kr.com/feed
"""

import news_utils

logger = news_utils.setup_logger(__name__)


def get_today_news_file():
    """获取今天的 36kr 文件名"""
    return f"36kr_{news_utils.current_date_formatted()}.md"


def fetch_news():
    """抓取 36氪新闻"""
    logger.info("开始处理 36氪新闻源")
    
    entries = news_utils.get_rss_entries("https://36kr.com/feed", limit=20)
    if not entries:
        logger.warning("没有获取到 36kr 的 RSS 条目")
        return

    final_contents = []

    for i, entry in enumerate(entries):
        title = entry.get("title", "无标题")
        link = entry.get("link", "无链接")
        summary = entry.get("summary", "无摘要")
        
        # 转换 HTML 摘要为 Markdown
        if summary:
            summary = news_utils.convert_html_to_markdown(summary)
            if len(summary) > 300:
                summary = summary[:300] + "..."

        final_contents.append(f"### {i + 1}. [{title}]({link})\n")
        if summary and len(summary) > 10:
            final_contents.append(f"> {summary}\n")
        final_contents.append("---\n")

    # 保存到文件
    filename = get_today_news_file()
    content = "\n".join(final_contents)
    if news_utils.put_local_file_with_today(filename, content):
        logger.info(f"✓ 36氪新闻已保存: {filename}")
    else:
        logger.error(f"✗ 无法保存 36氪新闻: {filename}")


def get_today_news_content() -> str:
    """获取今天的 36kr 内容"""
    filename = get_today_news_file()
    content = news_utils.get_local_file_with_today(filename)
    if content:
        logger.info(f"今天的 36kr 已存在: {filename}")
        return content

    fetch_news()

    content = news_utils.get_local_file_with_today(filename)
    return content or ""


if __name__ == "__main__":
    fetch_news()