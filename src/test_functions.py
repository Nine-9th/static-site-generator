import unittest

from functions import (
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_delimiter,
)
from textnode import TextNode, TextType


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_splits_formatted_text(self):
        nodes = [TextNode("This is **bold** text", TextType.TEXT)]

        self.assertEqual(
            split_nodes_delimiter(nodes, "**", TextType.BOLD),
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" text", TextType.TEXT),
            ],
        )

    def test_splits_multiple_formatted_segments(self):
        nodes = [TextNode("**bold** and **more bold**", TextType.TEXT)]

        self.assertEqual(
            split_nodes_delimiter(nodes, "**", TextType.BOLD),
            [
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("more bold", TextType.BOLD),
            ],
        )

    def test_supports_other_delimiters_and_text_types(self):
        nodes = [TextNode("This is _italic_ text", TextType.TEXT)]

        self.assertEqual(
            split_nodes_delimiter(nodes, "_", TextType.ITALIC),
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" text", TextType.TEXT),
            ],
        )

    def test_preserves_non_text_nodes_as_is(self):
        node = TextNode("already italic", TextType.ITALIC)

        result = split_nodes_delimiter([node], "**", TextType.BOLD)

        self.assertIs(result[0], node)

    def test_omits_empty_segments(self):
        nodes = [TextNode("**bold**", TextType.TEXT)]

        self.assertEqual(
            split_nodes_delimiter(nodes, "**", TextType.BOLD),
            [TextNode("bold", TextType.BOLD)],
        )

    def test_raises_for_unmatched_delimiter(self):
        nodes = [TextNode("This is **unclosed", TextType.TEXT)]

        with self.assertRaisesRegex(ValueError, "unmatched delimiter"):
            split_nodes_delimiter(nodes, "**", TextType.BOLD)


class TestMarkdownExtraction(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )

        self.assertListEqual(
            [("image", "https://i.imgur.com/zjjcJKZ.png")], matches
        )

    def test_extracts_multiple_markdown_images(self):
        text = (
            "![rick roll](https://i.imgur.com/aKaOqIh.gif) and "
            "![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        )

        self.assertListEqual(
            [
                ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
                ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
            ],
            extract_markdown_images(text),
        )

    def test_returns_empty_list_when_no_images_exist(self):
        self.assertListEqual(extract_markdown_images("plain text"), [])

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a link [to boot dev](https://www.boot.dev)"
        )

        self.assertListEqual(
            [("to boot dev", "https://www.boot.dev")], matches
        )

    def test_extracts_multiple_markdown_links(self):
        text = (
            "[to boot dev](https://www.boot.dev) and "
            "[to youtube](https://www.youtube.com/@bootdotdev)"
        )

        self.assertListEqual(
            [
                ("to boot dev", "https://www.boot.dev"),
                ("to youtube", "https://www.youtube.com/@bootdotdev"),
            ],
            extract_markdown_links(text),
        )

    def test_does_not_extract_images_as_links(self):
        self.assertListEqual(
            [("docs", "https://docs.example.com")],
            extract_markdown_links(
                "![logo](https://example.com/logo.png) [docs](https://docs.example.com)"
            ),
        )

    def test_returns_empty_list_when_no_links_exist(self):
        self.assertListEqual(extract_markdown_links("plain text"), [])


if __name__ == "__main__":
    unittest.main()
