import sys
import types
import unittest


def _install_dify_plugin_stubs() -> None:
    dify_plugin = types.ModuleType("dify_plugin")

    class FakeTool:
        def create_variable_message(self, name, value):
            return {"type": "variable", "name": name, "value": value}

    dify_plugin.Tool = FakeTool

    entities_module = types.ModuleType("dify_plugin.entities")
    tool_module = types.ModuleType("dify_plugin.entities.tool")

    class ToolInvokeMessage(dict):
        pass

    tool_module.ToolInvokeMessage = ToolInvokeMessage

    sys.modules["dify_plugin"] = dify_plugin
    sys.modules["dify_plugin.entities"] = entities_module
    sys.modules["dify_plugin.entities.tool"] = tool_module


_install_dify_plugin_stubs()

from tools.url_extractor import UrlExtractorTool


class UrlExtractorToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = UrlExtractorTool()

    def test_normalize_url_removes_trailing_punctuation(self) -> None:
        normalized = self.tool._normalize_url("https://example.com/path?q=1).,")

        self.assertEqual(normalized, "https://example.com/path?q=1")

    def test_normalize_url_keeps_balanced_parentheses(self) -> None:
        normalized = self.tool._normalize_url("https://example.com/path(test)")

        self.assertEqual(normalized, "https://example.com/path(test)")

    def test_extract_urls_deduplicates_and_preserves_order(self) -> None:
        text = (
            "See https://example.com/a, https://example.com/b). "
            "Again https://example.com/a and https://example.com/c!"
        )

        urls = self.tool._extract_urls(text)

        self.assertEqual(
            urls,
            [
                "https://example.com/a",
                "https://example.com/b",
                "https://example.com/c",
            ],
        )

    def test_invoke_yields_urls_and_count(self) -> None:
        messages = list(
            self.tool._invoke(
                {
                    "input": "Links: https://example.com/a and https://example.com/b).",
                }
            )
        )

        self.assertEqual(
            messages,
            [
                {
                    "type": "variable",
                    "name": "urls",
                    "value": ["https://example.com/a", "https://example.com/b"],
                },
                {"type": "variable", "name": "count", "value": 2},
            ],
        )


if __name__ == "__main__":
    unittest.main()
