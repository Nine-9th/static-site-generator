import unittest

from leafnode import LeafNode
from textnode import TextNode, TextType, text_node_to_html_node


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_not_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a different text node", TextType.BOLD)
        self.assertNotEqual(node, node2)
        
    def test_repr(self):
        node = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(repr(node), "TextNode(This is a text node, TextType.BOLD, None)")

    def test_str(self):
        node = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(str(node), "TextNode(This is a text node, TextType.BOLD, None)")

    def test_text_type_returns_raw_text_leaf_node(self):
        node = text_node_to_html_node(TextNode("plain text", TextType.TEXT))

        self.assertIsInstance(node, LeafNode)
        self.assertIsNone(node.tag)
        self.assertEqual(node.value, "plain text")

    def test_bold_type_returns_b_tag(self):
        self.assertEqual(
            text_node_to_html_node(TextNode("bold", TextType.BOLD)).to_html(),
            "<b>bold</b>",
        )

    def test_italic_type_returns_i_tag(self):
        self.assertEqual(
            text_node_to_html_node(TextNode("italic", TextType.ITALIC)).to_html(),
            "<i>italic</i>",
        )

    def test_code_type_returns_code_tag(self):
        self.assertEqual(
            text_node_to_html_node(TextNode("code", TextType.CODE)).to_html(),
            "<code>code</code>",
        )

    def test_link_type_returns_anchor_with_href(self):
        node = text_node_to_html_node(
            TextNode("Boot.dev", TextType.LINK, "https://boot.dev")
        )

        self.assertEqual(node.tag, "a")
        self.assertEqual(node.value, "Boot.dev")
        self.assertEqual(node.props, {"href": "https://boot.dev"})
        self.assertEqual(
            node.to_html(),
            '<a href="https://boot.dev">Boot.dev</a>',
        )

    def test_image_type_returns_img_with_src_and_alt(self):
        node = text_node_to_html_node(
            TextNode("A logo", TextType.IMAGE, "logo.png")
        )

        self.assertEqual(node.tag, "img")
        self.assertEqual(node.value, "")
        self.assertEqual(node.props, {"src": "logo.png", "alt": "A logo"})
        self.assertEqual(
            node.to_html(),
            '<img src="logo.png" alt="A logo"></img>',
        )

    def test_unsupported_type_raises_value_error(self):
        node = TextNode("unknown", object())

        with self.assertRaises(ValueError):
            text_node_to_html_node(node)

    
if __name__ == "__main__":
    unittest.main()