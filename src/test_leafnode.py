import unittest

from leafnode import LeafNode


class TestLeafNode(unittest.TestCase):
    def test_missing_value_raises_value_error(self):
        with self.assertRaises(ValueError):
            LeafNode("p").to_html()

    def test_without_tag_returns_raw_text(self):
        self.assertEqual(LeafNode(value="plain text").to_html(), "plain text")

    def test_renders_tag(self):
        self.assertEqual(LeafNode("p", "hello").to_html(), "<p>hello</p>")

    def test_renders_props(self):
        node = LeafNode("a", "link", {"href": "https://example.com"})

        self.assertEqual(
            node.to_html(),
            '<a href="https://example.com">link</a>',
        )

    def test_empty_value_is_rendered(self):
        self.assertEqual(LeafNode("p", "").to_html(), "<p></p>")


if __name__ == "__main__":
    unittest.main()