"""
阮一峰的网络日志 RSS 源 - https://www.ruanyifeng.com/blog/atom.xml
"""

from datetime import datetime, timedelta

import news_utils

logger = news_utils.setup_logger(__name__)

RSS_URL = "https://www.ruanyifeng.com/blog/atom.xml"


def fetch_news(limit: int = 5):
    """抓取阮一峰博客最新文章（只获取最近7天内的）"""
    logger.info("开始抓取阮一峰的网络日志")
    
    entries = news_utils.get_rss_entries(RSS_URL, limit=limit * 3)  # 多获取一些以便过滤
    if not entries:
        logger.warning("没有获取到阮一峰博客文章")
        return
    
    file_contents = []
    file_contents.append(f"# 阮一峰的网络日志 - {news_utils.current_date_formatted()}\n\n")
    
    count = 0
    seven_days_ago = datetime.now() - timedelta(days=7)
    
    for entry in entries:
        if count >= limit:
            break
        
        title = entry.get("title", "无标题")
        link = entry.get("link", "无链接")
        summary = entry.get("summary", "无摘要")
        publish_time = news_utils.get_entry_datetime(entry)
        
        # 只获取最近7天内的文章
        if publish_time and publish_time < seven_days_ago:
            continue
        
        # 转换 HTML 摘要为 Markdown
        if summary:
            summary = news_utils.convert_html_to_markdown(summary)
            # 截断过长的摘要
            if len(summary) > 600:
                summary = summary[:600] + "..."
        
        publish_time_str = news_utils.get_entry_datetime_formated(entry)
        
        file_contents.append(f"### {count + 1}. [{title}]({link})\n\n")
        
        if summary and len(summary) > 10:
            file_contents.append(f"> {summary}\n\n")
        
        file_contents.append(f"<sub>发布时间: {publish_time_str}</sub>\n\n")
        file_contents.append("---\n\n")
        
        count += 1
    
    if count == 0:
        file_contents.append("最近7天没有新文章发布\n")
    
    # 保存到文件
    filename = get_today_news_file()
    full_content = "\n".join(file_contents)
    if news_utils.put_local_file_with_today(filename, full_content):
        logger.info(f"阮一峰博客文章已保存: {filename}")
    else:
        logger.error(f"无法保存阮一峰博客文章: {filename}")


def get_today_news_file() -> str:
    """获取今天的阮一峰博客文件名"""
    return f"ruanyifeng_{news_utils.current_date_formatted()}.md"


def get_today_news_content() -> str:
    """获取今天的阮一峰博客内容"""
    filename = get_today_news_file()
    content = news_utils.get_local_file_with_today(filename)
    if content:
        logger.info(f"今天的阮一峰博客文章已存在: {filename}")
        return content
    
    logger.info(f"今天的阮一峰博客文章不存在，开始抓取: {filename}")
    fetch_news()
    
    content = news_utils.get_local_file_with_today(filename)
    return content or ""


if __name__ == "__main__":
    fetch_news(limit=3)