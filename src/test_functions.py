import unittest

from functions import split_nodes_delimiter
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


if __name__ == "__main__":
    unittest.main()
