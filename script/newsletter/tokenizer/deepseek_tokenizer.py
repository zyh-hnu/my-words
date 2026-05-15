import os

from tokenizers import Tokenizer

chat_tokenizer_dir = os.path.dirname(os.path.abspath(__file__))
_tokenizer: Tokenizer | None = None


def _get_tokenizer() -> Tokenizer:
    global _tokenizer
    if _tokenizer is None:
        _tokenizer = Tokenizer.from_file(os.path.join(chat_tokenizer_dir, "tokenizer.json"))
    return _tokenizer


def calculate_tokenizer(msg: str) -> int:
    tokenizer = _get_tokenizer()
    result = tokenizer.encode(msg)
    return len(result.ids)


if __name__ == "__main__":
    print(calculate_tokenizer("你好，世界！"))
