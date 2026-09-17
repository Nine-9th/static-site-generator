import unittest
from parentnode import ParentNode
from leafnode import LeafNode

class TestParentNode(unittest.TestCase):
    def test_requires_tag(self):
        with self.assertRaises(TypeError):
            ParentNode(children=[])

    def test_requires_children(self):
        with self.assertRaises(TypeError):
            ParentNode("div")

    def test_does_not_store_a_value(self):
        node = ParentNode("div", [])

        self.assertIsNone(node.value)

    def test_renders_one_child(self):
        child_node = LeafNode("span", "child")

        self.assertEqual(
            ParentNode("div", [child_node]).to_html(),
            "<div><span>child</span></div>",
        )

    def test_renders_multiple_children_in_order(self):
        children = [
            LeafNode("span", "first"),
            LeafNode("span", "second"),
            LeafNode("span", "third"),
        ]

        self.assertEqual(
            ParentNode("div", children).to_html(),
            "<div><span>first</span><span>second</span><span>third</span></div>",
        )

    def test_renders_no_children(self):
        self.assertEqual(ParentNode("div", []).to_html(), "<div></div>")

    def test_renders_props(self):
        node = ParentNode("div", [], {"class": "container", "id": "main"})

        self.assertEqual(
            node.to_html(),
            '<div class="container" id="main"></div>',
        )

    def test_renders_nested_parent_nodes(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])

        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_renders_multiple_nested_parent_nodes(self):
        first_branch = ParentNode("li", [LeafNode("a", "first")])
        second_branch = ParentNode("li", [LeafNode("a", "second")])
        list_node = ParentNode("ul", [first_branch, second_branch])

        self.assertEqual(
            list_node.to_html(),
            "<ul><li><a>first</a></li><li><a>second</a></li></ul>",
        )

    def test_missing_tag_raises_value_error_when_rendering(self):
        with self.assertRaises(ValueError):
            ParentNode(None, []).to_html()

    def test_missing_children_raises_value_error_when_rendering(self):
        with self.assertRaises(ValueError):
            ParentNode("div", None).to_html()


if __name__ == "__main__":
    unittest.main()

