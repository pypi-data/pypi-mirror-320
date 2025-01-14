from docutils import nodes
from typing import Dict, Any, Optional
import re


def convert_to_ast(node: nodes.Node) -> Optional[Dict[str, Any]]:
    def text_handler(n: nodes.Text) -> Dict[str, str]:        
        return {"type": "text", "value": n.astext()}

    def title_handler(n: nodes.title) -> Dict[str, Any]:
        separator = node.get('separator', '-')
        header_type = node.get('header_type')
        return {
            "type": "element",
            "tagName": "h",
            "properties": {"separator": separator, "header_type": header_type},
            "children": [convert_to_ast(child) for child in n.children]
        }

    def paragraph_handler(n: nodes.paragraph) -> Dict[str, Any]:
        num = 0
        paragraph_text = []
        properties = {}
        for child in n.children:
            node = convert_to_ast(child)

            if node is None:
                return {
                    "type": "element",
                    "tagName": "None",
                }

            if node.get("type") != "text":
                num += 1
                tag_name = node['tagName']
                custom_tag = f"{tag_name}{num}"

                if 'children' in node:
                    children_string = node['children'][0]['value']
                else:
                    children_string = ''

                if 'properties' in node:
                    properties[custom_tag] = node['properties']

                paragraph_text.append(f"{{{tag_name}{num}}}{children_string}{{/{tag_name}{num}}}")
            else:
                paragraph_text.append(node.get('value'))
            
        value = " ".join(paragraph_text)
        return {
            "type": "element",
            "tagName": "p",
            "properties": properties,
            "children": [{"type": "text", "value": value}]
        }
    
    def document_handler(n: nodes.document) -> Dict[str, Any]:
        return {"type": "root", "children": [convert_to_ast(child) for child in n.children]}
    
    def list_item_handler(n: nodes.list_item) -> Dict[str, Any]:
        separator = node.get('separator', '-')
        return {"type": "element", "tagName": "li", "properties": {"separator": separator}, "children": [convert_to_ast(child) for child in n.children]}
    
    def list_handler(n: nodes.list_item) -> Dict[str, Any]:
        return {"type": "element", "tagName": "ul", "properties": {}, "children": [convert_to_ast(child) for child in n.children]}
    
    def section_handler(n: nodes.section) -> Dict[str, Any]:
        return {"type": "element", "tagName": "section", "properties": {}, "children": [convert_to_ast(child) for child in n.children]}
    
    def strong_handler(n: nodes.strong) -> Dict[str, Any]:
        return {
            "type": "element",
            "tagName": "strong",
            "properties": {"separator": "**"},
            "children": [convert_to_ast(child) for child in n.children]
        }
    
    def comment_handler(n: nodes.comment) -> Dict[str, Any]:
        return {
            "type": "element",
            "tagName": "comment",
            "properties": {"separator": ".."},
            "children": [convert_to_ast(child) for child in n.children]
        }
    
    def system_message_handler(n: nodes.system_message) -> Dict[str, Any]:
        if len(n.children) > 1:
            return {
                "type": "element",
                "tagName": "system_message",
                "properties": {},
                "children": [{"type": "text", "value": n.children[1].astext()}]
            }
        else:
            return {}
    
    def table_handler(n: nodes.table) -> Dict[str, Any]:
        list_table = node.get('list-table', None)
        return {"type": "element", "tagName": "table", "properties": {"list_table": list_table}, "children": [convert_to_ast(child) for child in n.children]}
    
    def tgroup_handler(n: nodes.tgroup) -> Dict[str, Any]:
        return {"type": "element", "tagName": "tgroup", "properties": {}, "children": [convert_to_ast(child) for child in n.children]}
    
    def thead_handler(n: nodes.thead) -> Dict[str, Any]:
        return {"type": "element", "tagName": "thead", "properties": {}, "children": [convert_to_ast(child) for child in n.children]}
    
    def row_handler(n: nodes.row) -> Dict[str, Any]:
        return {"type": "element", "tagName": "row", "properties": {}, "children": [convert_to_ast(child) for child in n.children]}
    
    def entry_handler(n: nodes.entry) -> Dict[str, Any]:
        return {"type": "element", "tagName": "entry", "properties": {}, "children": [convert_to_ast(child) for child in n.children]}
    
    def tbody_handler(n: nodes.tbody) -> Dict[str, Any]:
        return {"type": "element", "tagName": "tbody", "properties": {}, "children": [convert_to_ast(child) for child in n.children]}
    
    def colspec_handler(n: nodes.colspec) -> Dict[str, Any]:
        return {"type": "element", "tagName": "tbody", "properties": {}, "children": []}
    
    def image_handler(n: nodes.image) -> Dict[str, Any]:
        text = n.rawsource
        pattern = r"\.\. image:: (\S+)\n\s+:width:\s+(\S+)\n\s+:alt:\s+(.+)"

        match = re.match(pattern, text)
        src = ""
        width = ""
        alt = ""
        if match:
            src, width, alt = match.groups()

        custom_tag = "image0"

        return {"type": "element", "tagName": "p", "properties": {}, "children": [{"type": "text", "value": custom_tag, "tags": {custom_tag: {"src": src, "width": width, "alt": alt}}}]}
    
    def reference_handler(n: nodes.reference) -> Dict[str, Any]:
        label = n.astext()
        cleaned_string = n.rawsource.replace('`', '').replace('__', '')
        url = cleaned_string.replace(label, '').strip()
        href_obj = {"href": url}

        return {
            "type": "element",
            "tagName": "reference",
            "properties": href_obj,
            "children": [convert_to_ast(child) for child in n.children]
        }
    
    def literal_handler(n: nodes.literal) -> Dict[str, Any]:
        return {
            "type": "element",
            "tagName": "literal",
            "properties": {},
            "children": [convert_to_ast(child) for child in n.children]
        }
    
    def emphasis_handler(n: nodes.emphasis) -> Dict[str, Any]:
        return {
            "type": "element",
            "tagName": "emphasis",
            "properties": {},
            "children": [convert_to_ast(child) for child in n.children]
        }
    
    def target_handler(n: nodes.target) -> Dict[str, Any]:
        return {
            "type": "element",
            "tagName": "target",
            "properties": {},
            "children": [{"type": "text", "value": n.rawsource}]
        }
    
    def important_handler(n: nodes.important) -> Dict[str, Any]:
        return {
            "type": "element",
            "tagName": "important",
            "properties": {},
            "children": [{"type": "text", "value": n.rawsource}]
        }
    
    def note_handler(n: nodes.note) -> Dict[str, Any]:
        return {
            "type": "element",
            "tagName": "note",
            "properties": {},
            "children": [{"type": "text", "value": n.rawsource}]
        }

    handlers_node_types = {
        nodes.document: document_handler,
        nodes.Text: text_handler,
        nodes.title: title_handler,
        nodes.paragraph: paragraph_handler,
        nodes.list_item: list_item_handler,
        nodes.option_list_item: list_item_handler,
        nodes.definition_list_item: list_item_handler,
        nodes.enumerated_list: list_handler,
        nodes.definition_list: list_handler,
        nodes.option_list: list_handler,
        nodes.bullet_list: list_handler,
        nodes.field_list: list_handler,
        nodes.section: section_handler,
        nodes.strong: strong_handler,
        nodes.comment: comment_handler,
        nodes.system_message: system_message_handler,
        nodes.table: table_handler,
        nodes.tgroup: tgroup_handler,
        nodes.thead: thead_handler,
        nodes.row: row_handler,
        nodes.entry: entry_handler,
        nodes.tbody: tbody_handler,
        nodes.colspec: colspec_handler,
        nodes.image: image_handler,
        nodes.reference: reference_handler,
        nodes.literal: literal_handler,
        nodes.emphasis: emphasis_handler,
        nodes.target: target_handler,
        nodes.important: important_handler,
        nodes.note: note_handler
    }

    for node_type, handler in handlers_node_types.items():
        if isinstance(node, node_type):
            return handler(node)
    
    return None

