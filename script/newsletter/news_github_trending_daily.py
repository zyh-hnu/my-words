"""GitHub 每日趋势 RSS 源 - https://mshibanami.github.io/GitHubTrendingRSS/daily/all.xml"""

import news_utils

logger = news_utils.setup_logger(__name__)

RSS_URL = "https://mshibanami.github.io/GitHubTrendingRSS/daily/all.xml"
LIMIT = 20


def fetch_news():
    """抓取 GitHub Trending 内容"""
    logger.info("开始获取 GitHub 每日趋势")

    entries = news_utils.get_rss_entries(RSS_URL, limit=LIMIT)
    if not entries:
        logger.error("没有获取到 GitHub Trending RSS 条目")
        return

    # 构建内容
    final_content = [f"## GitHub Trending\n\n"]

    for index, entry in enumerate(entries):
        title = entry.get("title", "无标题")
        link = entry.get("link", "无链接")
        description = entry.get("summary", "无描述")

        # 转换 HTML 描述为 Markdown
        if description:
            description = news_utils.convert_html_to_markdown(description)
            # 截断过长的描述
            if len(description) > 500:
                description = description[:500] + "..."

        final_content.append(f"### {index + 1}. [{title}]({link})\n")
        if description and description != "无描述":
            final_content.append(f"> {description}\n")
        final_content.append("---\n")

    # 保存到文件
    filename = get_today_news_file()
    content = "\n".join(final_content)
    if news_utils.put_local_file_with_today(filename, content):
        logger.info(f"✓ GitHub Trending 已保存: {filename}")
    else:
        logger.error(f"✗ 无法保存 GitHub Trending: {filename}")


def get_today_news_file():
    """获取今天的 GitHub Trending 文件名"""
    return f"github_trending_{news_utils.current_date_formatted()}.md"


def get_today_news_content() -> str:
    """获取今天的 GitHub Trending 内容"""
    filename = get_today_news_file()
    content = news_utils.get_local_file_with_today(filename)
    if content:
        logger.info(f"今天的 GitHub Trending 已存在: {filename}")
        return content

    logger.info(f"今天的 GitHub Trending 不存在，开始抓取: {filename}")
    fetch_news()

    content = news_utils.get_local_file_with_today(filename)
    return content or ""


if __name__ == "__main__":
    fetch_news()