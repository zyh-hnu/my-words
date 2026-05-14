"""
个人日记/复盘功能模块
用于生成每日个人总结
"""

import os
from typing import Optional

import llm
import news_utils

logger = news_utils.setup_logger(__name__)


def get_diary_filename() -> str:
    """获取日记文件名"""
    return "diary.md"


def get_diary_template() -> str:
    """获取日记模板"""
    return """# {date} 每日复盘

## 今日完成

<!-- 列出今天完成的主要工作/任务 -->

- [ ] 
- [ ] 
- [ ] 

## 今日学习

<!-- 记录今天学到的新知识、新技能 -->

- 

## 今日思考

<!-- 记录今天的感悟、想法、反思 -->

> 

## 遇到的问题

<!-- 记录今天遇到的问题及解决方案 -->

| 问题 | 解决方案 |
|------|----------|
|      |          |

## 明日计划

<!-- 规划明天要做的事情 -->

- [ ] 
- [ ] 
- [ ] 

## 今日心情

<!-- 用一句话形容今天的心情/状态 -->

> 
"""


def create_diary_from_prompt(user_input: str) -> Optional[str]:
    """根据用户输入生成日记"""
    system_prompt = """你是一个专业的个人助理，帮助用户整理每日复盘日记。
请根据用户提供的信息，生成一份结构清晰、内容完整的每日复盘日记。

日记应该包含以下部分：
1. 今日完成 - 列出完成的主要工作/任务
2. 今日学习 - 记录学到的新知识
3. 今日思考 - 感悟、想法、反思
4. 遇到的问题 - 问题及解决方案
5. 明日计划 - 明天要做的事情
6. 今日心情 - 一句话形容今天的状态

请使用 Markdown 格式输出。"""

    user_prompt = f"""请根据以下信息生成今日的每日复盘日记：

{user_input}

请生成一份完整的每日复盘日记。"""

    return llm.one_shoot(system_prompt, user_prompt)


def generate_empty_diary() -> str:
    """生成空的日记模板"""
    today = news_utils.current_date_formatted()
    return get_diary_template().format(date=today)


def save_diary(content: str) -> bool:
    """保存日记到本地"""
    filename = get_diary_filename()
    return news_utils.put_local_file_with_today(filename, content)


def get_today_diary() -> Optional[str]:
    """获取今天的日记"""
    filename = get_diary_filename()
    return news_utils.get_local_file_with_today(filename)


def generate_diary(user_input: Optional[str] = None) -> bool:
    """生成日记
    
    Args:
        user_input: 用户输入的内容，如果为 None 则生成空模板
    
    Returns:
        bool: 是否成功生成并保存
    """
    # 检查今天是否已经有日记
    existing_diary = get_today_diary()
    if existing_diary:
        logger.info(f"今天的日记已经存在，不重复生成")
        return True

    if user_input:
        # 根据用户输入生成日记
        diary_content = create_diary_from_prompt(user_input)
        if not diary_content:
            logger.error("生成日记失败")
            return False
    else:
        # 生成空模板
        diary_content = generate_empty_diary()

    if save_diary(diary_content):
        logger.info(f"✓ 今日日记已保存")
        return True
    else:
        logger.error(f"✗ 无法保存今日日记")
        return False


def generate_diary_profile():
    """生成日记主页"""
    newsletter_dir = news_utils.get_newsletter_directory()
    diary_files = []
    
    # 遍历所有日期目录，查找日记文件
    for date_dir in sorted(os.listdir(newsletter_dir), reverse=True):
        date_path = os.path.join(newsletter_dir, date_dir)
        if os.path.isdir(date_path):
            diary_path = os.path.join(date_path, get_diary_filename())
            if os.path.exists(diary_path):
                diary_files.append((date_dir, diary_path))

    if not diary_files:
        logger.warning("没有找到任何日记文件")
        return

    diary_homepage = ["# 每日复盘日记\n"]
    
    for i, (date, diary_path) in enumerate(diary_files):
        if i == 0:
            # 显示最新的日记内容
            with open(diary_path, "r", encoding="utf-8") as f:
                content = f.read()
            diary_homepage.append(content)
            diary_homepage.append("\n---\n")
            diary_homepage.append("## 往日日记\n")
        else:
            # 添加往日日记链接
            diary_homepage.append(f"- [{date}](./{date}/diary.md)\n")

    homepage_content = "\n".join(diary_homepage)

    homepage_file = os.path.join(newsletter_dir, "diary_homepage.md")
    with open(homepage_file, "w", encoding="utf-8") as file:
        file.write(homepage_content)
        logger.info(f"✓ 已生成日记主页: {homepage_file}")


if __name__ == "__main__":
    # 测试生成空日记模板
    print(generate_empty_diary())
