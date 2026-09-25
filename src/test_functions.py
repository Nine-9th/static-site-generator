import unittest

from functions import (
    BlockType,
    block_to_block_type,
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
    text_to_text_nodes,
    markdown_to_blocks,
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


class TestMarkdownNodeSplitting(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) "
            "and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )

        new_nodes = split_nodes_image([node])

        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode(
                    "image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"
                ),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with a [link](https://www.boot.dev) "
            "and another [link](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )

        new_nodes = split_nodes_link([node])

        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "link", TextType.LINK, "https://www.youtube.com/@bootdotdev"
                ),
            ],
            new_nodes,
        )

    def test_split_images_preserves_non_text_nodes(self):
        image_node = TextNode("already an image", TextType.IMAGE, "image.png")

        new_nodes = split_nodes_image([image_node])

        self.assertIs(new_nodes[0], image_node)

    def test_split_links_preserves_non_text_nodes(self):
        link_node = TextNode("already a link", TextType.LINK, "https://example.com")

        new_nodes = split_nodes_link([link_node])

        self.assertIs(new_nodes[0], link_node)

    def test_split_images_leaves_plain_text_unchanged(self):
        node = TextNode("plain text", TextType.TEXT)

        self.assertListEqual([node], split_nodes_image([node]))

    def test_split_links_does_not_split_images(self):
        node = TextNode("![logo](https://example.com/logo.png)", TextType.TEXT)

        self.assertListEqual([node], split_nodes_link([node]))


class TestTextToTextNodes(unittest.TestCase):
    def test_converts_mixed_markdown(self):
        text = (
            "This is **text** with an _italic_ word and a `code block` and an "
            "![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a "
            "[link](https://boot.dev)"
        )

        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode(
                    "obi wan image",
                    TextType.IMAGE,
                    "https://i.imgur.com/fJRm4Vk.jpeg",
                ),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            text_to_text_nodes(text),
        )

    def test_converts_plain_text(self):
        self.assertListEqual(
            [TextNode("plain text", TextType.TEXT)],
            text_to_text_nodes("plain text"),
        )

    def test_converts_multiple_same_type_nodes(self):
        self.assertListEqual(
            [
                TextNode("one ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("two", TextType.BOLD),
            ],
            text_to_text_nodes("one **bold** and **two**"),
        )


class TestMarkdownToBlocks(unittest.TestCase):
    def test_splits_markdown_into_blocks(self):
        markdown = (
            "# This is a heading\n\n"
            "This is a paragraph of text. It has some **bold** and _italic_ words inside of it.\n\n"
            "- This is the first list item in a list block\n"
            "- This is a list item\n"
            "- This is another list item"
        )

        self.assertListEqual(
            [
                "# This is a heading",
                "This is a paragraph of text. It has some **bold** and _italic_ words inside of it.",
                "- This is the first list item in a list block\n"
                "- This is a list item\n"
                "- This is another list item",
            ],
            markdown_to_blocks(markdown),
        )

    def test_strips_whitespace_from_each_block(self):
        markdown = "  first block  \n\n\tsecond block\t  "

        self.assertListEqual(
            ["first block", "second block"],
            markdown_to_blocks(markdown),
        )

    def test_ignores_empty_blocks_from_excessive_newlines(self):
        markdown = "\n\nfirst block\n\n\n\nsecond block\n\n"

        self.assertListEqual(
            ["first block", "second block"],
            markdown_to_blocks(markdown),
        )

    def test_preserves_single_newlines_inside_a_block(self):
        markdown = "- first item\n- second item"

        self.assertListEqual(
            ["- first item\n- second item"],
            markdown_to_blocks(markdown),
        )


class TestBlockToBlockType(unittest.TestCase):
    def test_identifies_headings(self):
        self.assertEqual(block_to_block_type("### Heading"), BlockType.HEADING)

    def test_identifies_code_blocks(self):
        block = "```\nprint('hello')\n```"

        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_identifies_quote_blocks(self):
        block = "> first quote\n> second quote"

        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_identifies_unordered_lists(self):
        block = "- first item\n- second item"

        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_identifies_ordered_lists(self):
        block = "1. first item\n2. second item\n3. third item"

        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_identifies_paragraphs(self):
        self.assertEqual(
            block_to_block_type("This is a normal paragraph."),
            BlockType.PARAGRAPH,
        )

    def test_heading_requires_hashes_followed_by_space(self):
        self.assertEqual(block_to_block_type("###Heading"), BlockType.PARAGRAPH)

    def test_heading_allows_at_most_six_hashes(self):
        self.assertEqual(
            block_to_block_type("####### Too many hashes"),
            BlockType.PARAGRAPH,
        )

    def test_code_block_requires_newline_after_opening_fence(self):
        self.assertEqual(block_to_block_type("```code```"), BlockType.PARAGRAPH)

    def test_quote_requires_every_line_to_start_with_greater_than(self):
        block = "> quoted line\nnot quoted"

        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_must_start_at_one_and_increment(self):
        self.assertEqual(
            block_to_block_type("2. first item\n3. second item"),
            BlockType.PARAGRAPH,
        )
        self.assertEqual(
            block_to_block_type("1. first item\n3. skipped item"),
            BlockType.PARAGRAPH,
        )


if __name__ == "__main__":
    unittest.main()
