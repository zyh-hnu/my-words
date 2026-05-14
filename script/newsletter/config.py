import os

import dotenv


class Settings:
    def __init__(self):
        dotenv.load_dotenv()

        self.openai_api_key = self._must_get_env("OPENAI_API_KEY")
        self.openai_base_url = self._must_get_env("OPENAI_BASE_URL")

        # Newsletter 输出目录，默认为项目根目录下的 newsletters
        self.newsletter_dir = os.getenv("NEWSLETTER_DIR", self._get_default_newsletter_dir())

        # PushDeer 推送（可选）
        self.push_deer_key = os.getenv("PUSH_DEER_KEY", "")

    def _must_get_env(self, key: str) -> str:
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Environment variable '{key}' is not set.")
        return value

    def _get_default_newsletter_dir(self) -> str:
        """获取默认的 newsletter 目录（项目根目录下的 newsletters）"""
        # 从当前文件位置向上导航到项目根目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_dir = os.path.dirname(current_dir)
        project_root = os.path.dirname(script_dir)
        return os.path.join(project_root, "newsletters")


settings = Settings()