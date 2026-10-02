import tiktoken

class TokenCounter:
    def __init__(self):
        self.encoder = tiktoken.get_encoding("cl100k_base")

    def count(self, text: str) -> int:
        return len(self.encoder.encode(text))

    def truncate(self, text: str, max_tokens: int) -> str:
        encoded = self.encoder.encode(text)
        if len(encoded) <= max_tokens:
            return text
        truncated = encoded[:max_tokens]
        return self.encoder.decode(truncated)

    def get_last_tokens(self, text: str, num_tokens: int) -> str:
        encoded = self.encoder.encode(text)
        if len(encoded) <= num_tokens:
            return text
        last_tokens = encoded[-num_tokens:]
        return self.encoder.decode(last_tokens)

