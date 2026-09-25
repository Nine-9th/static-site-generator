from enum import Enum
import re

from htmlnode import HTMLNode
from parentnode import ParentNode
from textnode import TextNode, TextType, text_node_to_html_node

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


def text_to_children(text: str) -> list[HTMLNode]:
    text_nodes = text_to_text_nodes(text)
    return [text_node_to_html_node(node) for node in text_nodes]


def heading_to_html_node(block: str) -> HTMLNode:
    heading_marker, heading_text = block.split(" ", 1)
    return ParentNode(f"h{len(heading_marker)}", text_to_children(heading_text))


def code_to_html_node(block: str) -> HTMLNode:
    code_text = block[4:-3]
    code_child = text_node_to_html_node(TextNode(code_text, TextType.TEXT))
    code_node = ParentNode("code", [code_child])
    return ParentNode("pre", [code_node])


def quote_to_html_node(block: str) -> HTMLNode:
    quote_lines = [line[1:].lstrip() for line in block.splitlines()]
    quote_text = " ".join(quote_lines)
    return ParentNode("blockquote", text_to_children(quote_text))


def unordered_list_to_html_node(block: str) -> HTMLNode:
    list_items = [
        ParentNode("li", text_to_children(line[2:]))
        for line in block.splitlines()
    ]
    return ParentNode("ul", list_items)


def ordered_list_to_html_node(block: str) -> HTMLNode:
    list_items = [
        ParentNode("li", text_to_children(re.sub(r"^\d+\. ", "", line)))
        for line in block.splitlines()
    ]
    return ParentNode("ol", list_items)


def paragraph_to_html_node(block: str) -> HTMLNode:
    paragraph_text = block.replace("\n", " ")
    return ParentNode("p", text_to_children(paragraph_text))


def block_to_html_node(block: str) -> HTMLNode:
    block_type = block_to_block_type(block)

    if block_type == BlockType.HEADING:
        return heading_to_html_node(block)
    if block_type == BlockType.CODE:
        return code_to_html_node(block)
    if block_type == BlockType.QUOTE:
        return quote_to_html_node(block)
    if block_type == BlockType.UNORDERED_LIST:
        return unordered_list_to_html_node(block)
    if block_type == BlockType.ORDERED_LIST:
        return ordered_list_to_html_node(block)
    return paragraph_to_html_node(block)


def markdown_to_html_node(markdown: str) -> HTMLNode:
    block_nodes = [block_to_html_node(block) for block in markdown_to_blocks(markdown)]
    return ParentNode("div", block_nodes)