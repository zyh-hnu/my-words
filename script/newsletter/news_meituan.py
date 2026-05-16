"""美团技术团队

https://tech.meituan.com/feed/

处理逻辑：获取发布日期为今天或昨天的文章
"""

from datetime import datetime, timedelta

import news_utils

logger = news_utils.setup_logger(__name__)


def get_today_news_file():
    """获取今天的美团技术文件名"""
    return f"meituan_{news_utils.current_date_formatted()}.md"


def fetch_news():
    """抓取美团技术团队文章"""
    logger.info("开始抓取美团技术团队今天发布的文章")
    
    entries = news_utils.get_rss_entries("https://tech.meituan.com/feed/", limit=30)
    if not entries:
        logger.warning("没有获取到任何文章")
        return

    final_contents = []
    current_date = datetime.now().strftime("%Y-%m-%d")
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    for entry in entries:
        published_datetime = news_utils.get_entry_datetime(entry)
        if not published_datetime:
            continue

        published_date = published_datetime.strftime("%Y-%m-%d")
        if published_date != current_date and published_date != yesterday_date:
            continue

        title = entry.get("title", "无标题")
        link = entry.get("link", "")
        summary = entry.get("summary", "")

        # 转换 HTML 摘要为 Markdown
        if summary:
            summary = news_utils.convert_html_to_markdown(summary)
            if len(summary) > 500:
                summary = summary[:500] + "..."

        logger.info(f"找到今天的文章: {title} ({link})")
        
        final_contents.append(f"### {title}\n\n> {published_date}\n\n")
        if summary and len(summary) > 10:
            final_contents.append(f"{summary}\n\n")
        final_contents.append(f"[阅读全文]({link})\n\n---\n\n")

    if not final_contents:
        logger.info("美团技术团队今天没有发布新文章")
        final_contents = ["今天没有新的文章发布"]

    # 保存到文件
    filename = get_today_news_file()
    full_content = "\n".join(final_contents)
    if news_utils.put_local_file_with_today(filename, full_content):
        logger.info(f"✓ 美团技术团队内容已保存: {filename}")
    else:
        logger.error(f"✗ 无法保存美团技术团队内容: {filename}")


def get_today_posts_content() -> str:
    """获取今天的美团技术内容"""
    filename = get_today_news_file()
    content = news_utils.get_local_file_with_today(filename)
    if content:
        logger.info(f"今天的美团技术已存在: {filename}")
        return content

    fetch_news()
    
    content = news_utils.get_local_file_with_today(filename)
    return content or ""


if __name__ == "__main__":
    print(get_today_posts_content())