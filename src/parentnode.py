from htmlnode import HTMLNode


class ParentNode(HTMLNode):
	def __init__(self, tag, children, props=None):
		super().__init__(tag, None, children, props)

	def to_html(self):
		if self.tag is None:
			raise ValueError("ParentNode must have a tag")
		if self.children is None:
			raise ValueError("ParentNode must have children")

		props_str = self.propts_to_html()
		children_str = "".join(child.to_html() for child in self.children)
		return f"<{self.tag}{props_str}>{children_str}</{self.tag}>"
