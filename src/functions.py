from textnode import TextNode, TextType


def split_nodes_delimiter(old_nodes: list[TextNode], delimiter: str, text_type: TextType) -> list[TextNode]:
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        parts = node.text.split(delimiter)
        if len(parts) % 2 == 0:
            raise ValueError(f"Invalid Markdown syntax: unmatched delimiter {delimiter!r}")

        for index, part in enumerate(parts):
            if not part:
                continue
            part_type = text_type if index % 2 else TextType.TEXT
            new_nodes.append(TextNode(part, part_type))
    return new_nodes