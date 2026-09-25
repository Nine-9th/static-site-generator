from enum import Enum
import re

from textnode import TextNode, TextType

class BlockType(Enum):
    PARAGRAPH = 1
    HEADING = 2
    CODE = 3
    QUOTE = 4
    UNORDERED_LIST = 5
    ORDERED_LIST = 6

def block_to_block_type(block: str) -> BlockType:
    if re.match(r"^#{1,6} .+", block):
        return BlockType.HEADING
    if block.startswith("```\n") and block.endswith("```"):
        return BlockType.CODE
    lines = block.splitlines()
    if lines and all(line.startswith(">") for line in lines):
        return BlockType.QUOTE
    if lines and all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST
    ordered_list = [re.match(r"^(\d+)\. ", line) for line in lines]
    if lines and all(match is not None for match in ordered_list):
        numbers = [int(match.group(1)) for match in ordered_list]
        if numbers == list(range(1, len(numbers) + 1)):
            return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH

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

def extract_markdown_images(text: str) -> list[tuple[str, str]]:
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)


def extract_markdown_links(text: str) -> list[tuple[str, str]]:
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        parts = extract_markdown_images(node.text)
        if not parts:
            new_nodes.append(node)
            continue

        last_index = 0
        for match in re.finditer(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", node.text):
            start, end = match.span()
            if start > last_index:
                new_nodes.append(TextNode(node.text[last_index:start], TextType.TEXT))
            alt_text, url = match.groups()
            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
            last_index = end

        if last_index < len(node.text):
            new_nodes.append(TextNode(node.text[last_index:], TextType.TEXT))

    return new_nodes

def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:  
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        parts = extract_markdown_links(node.text)
        if not parts:
            new_nodes.append(node)
            continue

        last_index = 0
        for match in re.finditer(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", node.text):
            start, end = match.span()
            if start > last_index:
                new_nodes.append(TextNode(node.text[last_index:start], TextType.TEXT))
            link_text, url = match.groups()
            new_nodes.append(TextNode(link_text, TextType.LINK, url))
            last_index = end

        if last_index < len(node.text):
            new_nodes.append(TextNode(node.text[last_index:], TextType.TEXT))

    return new_nodes

def text_to_text_nodes(text: str) -> list[TextNode]:
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    return split_nodes_link(nodes)

def markdown_to_blocks(markdown: str) -> list[str]:
    raw_blocks = markdown.split("\n\n")
    blocks = []

    for raw_block in raw_blocks:
        block = raw_block.strip()
        if block:
            blocks.append(block)

    return blocks