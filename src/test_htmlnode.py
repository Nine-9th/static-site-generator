import unittest
from htmlnode import HTMLNode


class TestHTMLNode(unittest.TestCase):
    def test_default_values(self):
        node = HTMLNode()

        self.assertIsNone(node.tag)
        self.assertIsNone(node.value)
        self.assertIsNone(node.children)
        self.assertIsNone(node.props)

    def test_stores_values(self):
        children = [HTMLNode("span", "hello")]
        props = {"href": "https://www.google.com"}
        node = HTMLNode("a", "Google", children, props)

        self.assertEqual(node.tag, "a")
        self.assertEqual(node.value, "Google")
        self.assertEqual(node.children, children)
        self.assertEqual(node.props, props)

    def test_props_to_html_without_props(self):
        self.assertEqual(HTMLNode().propts_to_html(), "")

    def test_props_to_html(self):
        node = HTMLNode(props={"href": "https://www.google.com", "target": "_blank"})

        self.assertEqual(
            node.propts_to_html(),
            ' href="https://www.google.com" target="_blank"',
        )

    def test_repr(self):
        node = HTMLNode("p", "Hello", [], {})

        self.assertEqual(
            repr(node),
            "HTMLNode(tag=p, value=Hello, children=[], props={})",
        )

    def test_to_html_is_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            HTMLNode().to_html()


if __name__ == "__main__":
    unittest.main()