import re
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


URL_PATTERN = re.compile(r"(?P<url>https?://[^\s<>\"']+)", re.IGNORECASE)
TRAILING_PUNCTUATION = ".,;:!?]}>'\""


class UrlExtractorTool(Tool):

    # テキストに含まれる URL を重複排除してリストで抽出
    def _extract_urls(self, text: str) -> list[str]:
        urls: list[str] = []
        seen: set[str] = set()

        for match in URL_PATTERN.finditer(text):
            candidate = self._normalize_url(match.group("url"))
            if not candidate or candidate in seen:
                continue

            seen.add(candidate)
            urls.append(candidate)

        return urls

    # URL 末尾の句読点や引用符、括弧を削除して正規化
    def _normalize_url(self, url: str) -> str:
        normalized = url.rstrip(TRAILING_PUNCTUATION)

        while normalized.endswith(")") and normalized.count("(") < normalized.count(
            ")"
        ):
            normalized = normalized[:-1]

        return normalized

    # ツールが呼び出されたときの実装
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # ツールの入力パラメーターからテキストを取得
        input_text = str(tool_parameters.get("input") or "")
        # テキストから URL を抽出
        urls = self._extract_urls(input_text)
        count = len(urls)

        # 抽出された URL とその数をツールの出力として返す
        yield self.create_variable_message("urls", urls)
        yield self.create_variable_message("count", count)
