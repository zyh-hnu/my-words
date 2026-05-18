"""Newsletter 生成模块 - 生成索引页"""

import os
import pathlib

import news_ai_news
import news_arxiv
import news_github_trending_daily
import news_ithome
import news_linuxdo
import news_meituan
import news_ruanyifeng
import news_shaoshupai
import news_36kr
import news_jiqizhixin
import news_utils
import news_v2ex
import news_zhihu

logger = news_utils.setup_logger(__name__)


def get_newsletter_filename() -> str:
    """获取 newsletter 文件名"""
    return "newsletter.md"


def get_newsletter_directory() -> str:
    """获取 newsletter 的目录"""
    return news_utils.get_newsletter_directory()


def _safe_fetch(fetch_fn, name: str) -> bool:
    """安全抓取，失败时返回 False"""
    try:
        fetch_fn()
        return True
    except Exception as e:
        logger.warning(f"获取 {name} 内容失败: {type(e).__name__}: {e}")
        return False


def generate_newsletter():
    """生成 newsletter 索引页"""
    newsletter_filename = get_newsletter_filename()
    if news_utils.get_local_file_with_today(newsletter_filename):
        logger.info(f"今天的 newsletter 已存在，不重复生成: {newsletter_filename}")
        return

    # 抓取所有新闻源（单个失败不影响其他）
    # 核心订阅
    _safe_fetch(news_ai_news.get_today_news_content, "AI News")
    _safe_fetch(news_github_trending_daily.get_today_news_content, "GitHub Trending")
    _safe_fetch(news_shaoshupai.get_today_news_content, "少数派")
    _safe_fetch(news_v2ex.get_today_news_content, "V2EX")
    _safe_fetch(news_meituan.get_today_posts_content, "美团技术")
    
    # 新增订阅源
    _safe_fetch(lambda: news_arxiv.fetch_all_arxiv_papers(limit_per_category=10), "arXiv 论文")
    _safe_fetch(news_linuxdo.get_today_news_content, "LinuxDo")
    _safe_fetch(news_ruanyifeng.get_today_news_content, "阮一峰博客")
    _safe_fetch(news_ithome.get_today_news_content, "IT之家")
    _safe_fetch(news_zhihu.get_today_news_content, "知乎热门")

    # 可选订阅源
    _safe_fetch(news_36kr.get_today_news_content, "36氪")
    _safe_fetch(news_jiqizhixin.get_today_news_content, "机器之心")

    # 生成索引页
    current_datetime = news_utils.current_datetime_formatted()
    contents = [
        f"# 今日技术 Newsletter - {news_utils.current_date_formatted()}\n",
        f"<sub>生成时间：{current_datetime}</sub>\n",
        "---\n",
    ]

    # AI News
    ai_news_file = news_ai_news.get_today_news_file()
    if news_utils.get_local_file_with_today(ai_news_file):
        contents.append(f"## AI 热点\n")
        contents.append(f"- [AINews](./{ai_news_file})\n")
        contents.append("\n---\n")

    # arXiv 论文
    arxiv_ai_file = news_arxiv.get_today_news_file("cs.AI")
    if news_utils.get_local_file_with_today(arxiv_ai_file):
        contents.append(f"## AI 论文\n")
        contents.append(f"- [arXiv AI](./{arxiv_ai_file})\n")
        arxiv_ml_file = news_arxiv.get_today_news_file("cs.LG")
        if news_utils.get_local_file_with_today(arxiv_ml_file):
            contents.append(f"- [arXiv ML](./{arxiv_ml_file})\n")
        arxiv_nlp_file = news_arxiv.get_today_news_file("cs.CL")
        if news_utils.get_local_file_with_today(arxiv_nlp_file):
            contents.append(f"- [arXiv NLP](./{arxiv_nlp_file})\n")
        contents.append("\n---\n")

    # GitHub Trending
    github_file = news_github_trending_daily.get_today_news_file()
    if news_utils.get_local_file_with_today(github_file):
        contents.append(f"## 开源项目\n")
        contents.append(f"- [GitHub Trending](./{github_file})\n")
        contents.append("\n---\n")

    # 少数派
    shaoshupai_file = news_shaoshupai.get_today_news_file()
    if news_utils.get_local_file_with_today(shaoshupai_file):
        contents.append(f"## 技术文章\n")
        contents.append(f"- [少数派](./{shaoshupai_file})\n")
        contents.append("\n---\n")

    # 阮一峰博客
    ruanyifeng_file = news_ruanyifeng.get_today_news_file()
    if news_utils.get_local_file_with_today(ruanyifeng_file):
        contents.append(f"- [阮一峰博客](./{ruanyifeng_file})\n")
        contents.append("\n---\n")

    # V2EX
    v2ex_file = news_v2ex.get_today_news_file("hot")
    if news_utils.get_local_file_with_today(v2ex_file):
        contents.append(f"## 技术讨论\n")
        contents.append(f"- [V2EX 最热](./{v2ex_file})\n")
    v2ex_tech_file = news_v2ex.get_today_news_file("tech")
    if news_utils.get_local_file_with_today(v2ex_tech_file):
        contents.append(f"- [V2EX 技术](./{v2ex_tech_file})\n")
    if contents[-1] != "---\n":
        contents.append("\n---\n")

    # LinuxDo
    linuxdo_file = news_linuxdo.get_today_news_file()
    if news_utils.get_local_file_with_today(linuxdo_file):
        contents.append(f"- [LinuxDo](./{linuxdo_file})\n")
        contents.append("\n---\n")

    # 知乎热门
    zhihu_file = news_zhihu.get_today_news_file()
    if news_utils.get_local_file_with_today(zhihu_file):
        contents.append(f"- [知乎热门](./{zhihu_file})\n")
        contents.append("\n---\n")

    # 美团技术
    meituan_file = news_meituan.get_today_news_file()
    if news_utils.get_local_file_with_today(meituan_file):
        contents.append(f"## 技术博客\n")
        contents.append(f"- [美团技术团队](./{meituan_file})\n")
        contents.append("\n---\n")

    # 36氪
    kr36_file = news_36kr.get_today_news_file()
    if news_utils.get_local_file_with_today(kr36_file):
        contents.append(f"## 商业科技\n")
        contents.append(f"- [36氪](./{kr36_file})\n")
        contents.append("\n---\n")

    # 机器之心
    jiqizhixin_file = news_jiqizhixin.get_today_news_file()
    if news_utils.get_local_file_with_today(jiqizhixin_file):
        contents.append(f"- [机器之心](./{jiqizhixin_file})\n")
    if contents[-1] == "---\n":
        contents.append("\n")
    contents.append("\n---\n")

    # IT之家
    ithome_file = news_ithome.get_today_news_file()
    if news_utils.get_local_file_with_today(ithome_file):
        contents.append(f"## 科技资讯\n")
        contents.append(f"- [IT之家](./{ithome_file})\n")
        contents.append("\n---\n")

    # 保存 newsletter
    if news_utils.put_local_file_with_today(newsletter_filename, "\n".join(contents)):
        logger.info(f"✓ 今日 newsletter 已保存: {newsletter_filename}")
    else:
        logger.error(f"✗ 无法保存今日 newsletter: {newsletter_filename}")


def generate_newsletter_profile():
    """生成 newsletter 主页"""
    newsletter_dir = get_newsletter_directory()
    newsletter_files = list(pathlib.Path(newsletter_dir).glob("**/newsletter.md"))
    newsletter_files.sort(key=lambda x: x.parent.absolute(), reverse=True)

    if not newsletter_files:
        logger.warning("没有找到任何 newsletter 文件")
        return

    newsletter_homepage = []
    
    for i, file in enumerate(newsletter_files):
        date_formatted = file.parent.name
        
        if i == 0:  # 处理最新的 newsletter
            content = file.read_text(encoding="utf-8")
            # 将所有相对路径链接都加上日期前缀
            content = content.replace("](./", f"](./{date_formatted}/")
            newsletter_homepage.append(content)
        
        if i == 1:  # 在第二个文件前添加往日新闻标题
            newsletter_homepage.append("\n# 往日新闻\n")
        
        if i > 0:  # 从第二个文件开始添加链接
            newsletter_homepage.append(f"#### [{date_formatted}](./{date_formatted}/newsletter.md)\n")

    homepage_content = "\n".join(newsletter_homepage)

    homepage_file = os.path.join(newsletter_dir, "homepage.md")
    with open(homepage_file, "w", encoding="utf-8") as file:
        file.write(homepage_content)
        logger.info(f"✓ 已生成 newsletter 主页: {homepage_file}")


def try_generate_newsletter():
    """生成 newsletter 和主页"""
    generate_newsletter()
    generate_newsletter_profile()


if __name__ == "__main__":
    try_generate_newsletter()
