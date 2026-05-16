"""
V2EX RSS Feed

最热帖子: https://www.v2ex.com/feed/tab/hot.xml
技术版: https://www.v2ex.com/feed/tab/tech.xml
"""

import news_utils

logger = news_utils.setup_logger(__name__)

# V2EX RSS 源配置
V2EX_FEEDS = {
    "hot": {"name": "最热", "url": "https://www.v2ex.com/feed/tab/hot.xml"},
    "tech": {"name": "技术", "url": "https://www.v2ex.com/feed/tab/tech.xml"},
}


def fetch_news(tab: str = "hot", limit: int = 30):
    """抓取 V2EX 指定版块的帖子
    
    Args:
        tab: 版块类型（hot 或 tech）
        limit: 限制获取的帖子数量
    """
    if tab not in V2EX_FEEDS:
        logger.error(f"未知的 V2EX 版块: {tab}")
        return
    
    feed_info = V2EX_FEEDS[tab]
    logger.info(f"获取 V2EX 论坛{feed_info['name']}帖子...")
    
    entries = news_utils.get_rss_entries(feed_info["url"], limit=limit)
    if not entries:
        logger.warning(f"没有获取到 V2EX {feed_info['name']}帖子")
        return None

    contents = [f"## V2EX {feed_info['name']}帖子\n"]
    for index, entry in enumerate(entries):
        title = entry.get("title", "无标题")
        link = entry.get("link", "无链接")
        author = entry.get("author", "无作者")
        published_format = news_utils.get_entry_datetime_formated(entry)
        summary = entry.get("summary", "无摘要")
        summary_md = news_utils.convert_html_to_markdown(summary)
        summary_md = summary_md.split("#1: ")[0]  # 只保留第一段内容
        summary_md = summary_md.replace("\n", "\n> ")  # 去除换行符，保持单行格式

        contents.append(f"### {index + 1}. [{title}]({link})\n\n> {summary_md} \n\n")
        contents.append(f"<sub>作者: {author} | 发布时间: {published_format}</sub>\n\n")
        contents.append("---\n\n")

    filename = get_today_news_file(tab)
    final_content = "\n".join(contents)
    if news_utils.put_local_file_with_today(filename, final_content):
        logger.info(f"V2EX {feed_info['name']}帖子已保存: {filename}")
    else:
        logger.error(f"无法保存 V2EX {feed_info['name']}帖子: {filename}")
        return


def fetch_hot_news(limit: int = 30):
    """抓取 V2EX 最热帖子"""
    fetch_news("hot", limit)


def fetch_tech_news(limit: int = 30):
    """抓取 V2EX 技术版帖子"""
    fetch_news("tech", limit)


def fetch_all_news(limit: int = 20):
    """抓取 V2EX 所有版块的帖子"""
    for tab in V2EX_FEEDS:
        fetch_news(tab, limit)


def get_today_news_file(tab: str = "hot") -> str:
    """获取今天的 V2EX 文件名"""
    return f"v2ex_{tab}_{news_utils.current_date_formatted()}.md"


def get_today_news_content(tab: str = "hot") -> str:
    """获取今天的 V2EX 内容"""
    filename = get_today_news_file(tab)
    content = news_utils.get_local_file_with_today(filename)
    if content:
        logger.info(f"今天的 V2EX {tab} 帖子已存在: {filename}")
        return content
    
    fetch_news(tab)
    
    content = news_utils.get_local_file_with_today(filename)
    if not content:
        logger.error(f"获取 V2EX {tab} 内容失败: {filename}")
        return ""
    return content


def get_all_today_news_content() -> str:
    """获取所有 V2EX 版块的内容"""
    all_content = []
    for tab in V2EX_FEEDS:
        content = get_today_news_content(tab)
        if content:
            all_content.append(content)
    return "\n\n".join(all_content)


if __name__ == "__main__":
    fetch_all_news(limit=10)
    logger.info("V2EX 论坛消息抓取完成")
