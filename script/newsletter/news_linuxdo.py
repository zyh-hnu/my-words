"""
LinuxDo 社区 RSS 源 - https://linux.do/latest.rss
"""

import news_utils

logger = news_utils.setup_logger(__name__)

RSS_URL = "https://linux.do/latest.rss"


def fetch_news(limit: int = 20):
    """抓取 LinuxDo 最新话题"""
    logger.info("开始抓取 LinuxDo 最新话题")
    
    entries = news_utils.get_rss_entries(RSS_URL, limit=limit)
    if not entries:
        logger.warning("没有获取到 LinuxDo 话题")
        return
    
    file_contents = []
    file_contents.append(f"# LinuxDo 社区热门话题 - {news_utils.current_date_formatted()}\n\n")
    
    for index, entry in enumerate(entries):
        title = entry.get("title", "无标题")
        link = entry.get("link", "无链接")
        summary = entry.get("summary", "无摘要")
        author = entry.get("author", "未知作者")
        publish_time = news_utils.get_entry_datetime_formated(entry)
        
        # 转换 HTML 摘要为 Markdown
        if summary:
            summary = news_utils.convert_html_to_markdown(summary)
            # 截断过长的摘要
            if len(summary) > 400:
                summary = summary[:400] + "..."
        
        file_contents.append(f"### {index + 1}. [{title}]({link})\n\n")
        
        if summary and len(summary) > 10:
            file_contents.append(f"> {summary}\n\n")
        
        file_contents.append(f"<sub>作者: {author} | 发布时间: {publish_time}</sub>\n\n")
        file_contents.append("---\n\n")
    
    # 保存到文件
    filename = get_today_news_file()
    full_content = "\n".join(file_contents)
    if news_utils.put_local_file_with_today(filename, full_content):
        logger.info(f"LinuxDo 话题已保存: {filename}")
    else:
        logger.error(f"无法保存 LinuxDo 话题: {filename}")


def get_today_news_file() -> str:
    """获取今天的 LinuxDo 文件名"""
    return f"linuxdo_{news_utils.current_date_formatted()}.md"


def get_today_news_content() -> str:
    """获取今天的 LinuxDo 内容"""
    filename = get_today_news_file()
    content = news_utils.get_local_file_with_today(filename)
    if content:
        logger.info(f"今天的 LinuxDo 话题已存在: {filename}")
        return content
    
    logger.info(f"今天的 LinuxDo 话题不存在，开始抓取: {filename}")
    fetch_news()
    
    content = news_utils.get_local_file_with_today(filename)
    return content or ""


if __name__ == "__main__":
    fetch_news(limit=5)