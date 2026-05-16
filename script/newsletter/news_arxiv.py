"""
arXiv 论文 RSS 源

- arXiv AI: https://rss.arxiv.org/rss/cs.AI
- arXiv ML: https://rss.arxiv.org/rss/cs.LG
- arXiv NLP: https://rss.arxiv.org/rss/cs.CL
"""

import news_utils

logger = news_utils.setup_logger(__name__)

# arXiv RSS 源配置
ARXIV_FEEDS = {
    "cs.AI": {"name": "AI", "url": "https://rss.arxiv.org/rss/cs.AI"},
    "cs.LG": {"name": "Machine Learning", "url": "https://rss.arxiv.org/rss/cs.LG"},
    "cs.CL": {"name": "NLP/CL", "url": "https://rss.arxiv.org/rss/cs.CL"},
}


def fetch_arxiv_papers(category: str, limit: int = 10):
    """抓取指定类别的 arXiv 论文
    
    Args:
        category: arXiv 类别（如 cs.AI、cs.LG、cs.CL）
        limit: 限制获取的论文数量
    """
    if category not in ARXIV_FEEDS:
        logger.error(f"未知的 arXiv 类别: {category}")
        return
    
    feed_info = ARXIV_FEEDS[category]
    logger.info(f"开始抓取 arXiv {feed_info['name']} 论文")
    
    entries = news_utils.get_rss_entries(feed_info["url"], limit=limit)
    if not entries:
        logger.warning(f"没有获取到 arXiv {feed_info['name']} 论文")
        return
    
    file_contents = []
    file_contents.append(f"# arXiv {feed_info['name']} - {news_utils.current_date_formatted()}\n\n")
    
    for index, entry in enumerate(entries):
        title = entry.get("title", "无标题")
        link = entry.get("link", "无链接")
        summary = entry.get("summary", "无摘要")
        authors = entry.get("author", "未知作者")
        
        # 清理标题（arXiv 标题可能包含类别前缀）
        if title.startswith(f"[{category}]"):
            title = title[len(f"[{category}]"):].strip()
        
        # 转换 HTML 摘要为 Markdown
        if summary:
            summary = news_utils.convert_html_to_markdown(summary)
            # 截断过长的摘要
            if len(summary) > 500:
                summary = summary[:500] + "..."
        
        file_contents.append(f"### {index + 1}. [{title}]({link})\n\n")
        
        if authors and authors != "未知作者":
            file_contents.append(f"**作者**: {authors}\n\n")
        
        if summary and len(summary) > 10:
            file_contents.append(f"> {summary}\n\n")
        
        file_contents.append("---\n\n")
    
    # 保存到文件
    filename = get_today_news_file(category)
    full_content = "\n".join(file_contents)
    if news_utils.put_local_file_with_today(filename, full_content):
        logger.info(f"arXiv {feed_info['name']} 论文已保存: {filename}")
    else:
        logger.error(f"无法保存 arXiv {feed_info['name']} 论文: {filename}")


def fetch_all_arxiv_papers(limit_per_category: int = 10):
    """抓取所有 arXiv 类别的论文"""
    for category in ARXIV_FEEDS:
        fetch_arxiv_papers(category, limit_per_category)


def get_today_news_file(category: str = "cs.AI") -> str:
    """获取今天的 arXiv 论文文件名"""
    return f"arxiv_{category.replace('.', '_')}_{news_utils.current_date_formatted()}.md"


def get_today_news_content(category: str = "cs.AI") -> str:
    """获取今天的 arXiv 论文内容"""
    filename = get_today_news_file(category)
    content = news_utils.get_local_file_with_today(filename)
    if content:
        logger.info(f"今天的 arXiv {category} 论文已存在: {filename}")
        return content
    
    logger.info(f"今天的 arXiv {category} 论文不存在，开始抓取: {filename}")
    fetch_arxiv_papers(category)
    
    content = news_utils.get_local_file_with_today(filename)
    return content or ""


def get_all_today_news_content() -> str:
    """获取所有 arXiv 类别的论文内容"""
    all_content = []
    for category in ARXIV_FEEDS:
        content = get_today_news_content(category)
        if content:
            all_content.append(content)
    return "\n\n".join(all_content)


if __name__ == "__main__":
    # 测试抓取 AI 论文
    fetch_arxiv_papers("cs.AI", limit=5)
