import sys

import diary
import news_utils
import newsletter
import push
from llm import get_llm_stats

logger = news_utils.setup_logger(__name__)


def main():
    """主函数，支持以下模式：
    - newsletter: 只生成技术 newsletter
    - diary: 只生成日记（需要用户输入）
    - all: 生成 newsletter + 空日记模板
    - 默认: 生成 newsletter + 空日记模板
    """
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    try:
        if mode in ["all", "newsletter"]:
            logger.info("开始生成技术 newsletter...")
            newsletter.try_generate_newsletter()
            logger.info("✓ 技术 newsletter 生成完成")

        if mode in ["all", "diary"]:
            logger.info("开始生成日记模板...")
            diary.generate_diary()
            diary.generate_diary_profile()
            logger.info("✓ 日记模板生成完成")

        logger.info(get_llm_stats())
        push.push_deer("今日内容已生成")
    except Exception as e:
        logger.error(f"生成过程中发生错误: {e}")
        push.push_deer(f"生成失败: {e}")
        logger.info(get_llm_stats())
        sys.exit(1)


if __name__ == "__main__":
    main()
