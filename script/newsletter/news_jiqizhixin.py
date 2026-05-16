"""
机器之心 RSS 源 - https://www.jiqizhixin.com/rss
"""

import news_utils

logger = news_utils.setup_logger(__name__)

RSS_URL = "https://www.jiqizhixin.com/rss"


def fetch_news(limit: int = 15):
    """抓取机器之心最新文章"""
    logger.info("开始抓取机器之心文章")
    
    entries = news_utils.get_rss_entries(RSS_URL, limit=limit)
    if not entries:
        logger.warning("没有获取到机器之心文章")
        return
    
    file_contents = []
    file_contents.append(f"# 机器之心 AI 前沿 - {news_utils.current_date_formatted()}\n\n")
    
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
            if len(summary) > 500:
                summary = summary[:500] + "..."
        
        file_contents.append(f"### {index + 1}. [{title}]({link})\n\n")
        
        if summary and len(summary) > 10:
            file_contents.append(f"> {summary}\n\n")
        
        file_contents.append(f"<sub>作者: {author} | 发布时间: {publish_time}</sub>\n\n")
        file_contents.append("---\n\n")
    
    # 保存到文件
    filename = get_today_news_file()
    full_content = "\n".join(file_contents)
    if news_utils.put_local_file_with_today(filename, full_content):
        logger.info(f"机器之心文章已保存: {filename}")
    else:
        logger.error(f"无法保存机器之心文章: {filename}")


def get_today_news_file() -> str:
    """获取今天的机器之心文件名"""
    return f"jiqizhixin_{news_utils.current_date_formatted()}.md"


def get_today_news_content() -> str:
    """获取今天的机器之心内容"""
    filename = get_today_news_file()
    content = news_utils.get_local_file_with_today(filename)
    if content:
        logger.info(f"今天的机器之心文章已存在: {filename}")
        return content
    
    logger.info(f"今天的机器之心文章不存在，开始抓取: {filename}")
    fetch_news()
    
    content = news_utils.get_local_file_with_today(filename)
    return content or ""


if __name__ == "__main__":
    fetch_news(limit=5)
