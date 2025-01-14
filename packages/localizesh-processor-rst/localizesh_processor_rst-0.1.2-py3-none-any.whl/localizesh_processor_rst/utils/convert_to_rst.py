from typing import Dict, List, Callable
from localizesh_sdk import LayoutRoot, LayoutElement, LayoutSegment, Segment
import re

def convert_to_rst(node: LayoutRoot, segments: List[Segment]) -> str:
    if node is None:
        return ""

    try:
        node_type = node["type"]
    except KeyError:
        return ""

    def convert_root(node: LayoutElement) -> str:
        children = [convert_to_rst(child, segments) for child in node.get("children", [])]
        return "\n".join(children)

    def convert_element(node: LayoutElement) -> str:
        tag_handlers = {
            "h": convert_h,
            "p": convert_p,
            "section": convert_section,
            "ul": convert_ul,
            "li": convert_li,
            "pre": convert_pre,
            "field_list": convert_field_list,
            "field": convert_field,
            "system_message": convert_system_message,
            "comment": convert_comment,
            "table": convert_table,
            "tgroup": convert_tgroup,
            "thead": convert_thead,
            "tbody": convert_tbody,
            "row": convert_row,
            "entry": convert_entry,
            "target": convert_target,
            "important": convert_important,
            "note": convert_note,
        }
        tag_name = node.get("tagName")
        if tag_name in tag_handlers:
            return tag_handlers[tag_name](node)
        return ""

    def convert_text(node: LayoutElement) -> str:
        return node.get("value", "")
    
    def convert_segment(node: LayoutSegment) -> str:
        segment_id = node.get("id")
        segment = next((seg for seg in segments if seg["id"] == segment_id), None)
    
        if segment is None:
            return "Segment not found"

        segment_text = segment.get("text", "")
        segment_tags = segment.get("tags", "")
        
        if segment_tags:
            for tag_key, tag_value in segment_tags.items():
                src = tag_value.get('src', '')
                width = tag_value.get('width', '')
                alt = tag_value.get('alt', '')
                rst_string = f".. image:: {src}\n  :width: {width}\n  :alt: {alt}"
                
                segment_text = segment_text.replace(tag_key, rst_string)

        return segment_text

    def convert_h(node: LayoutElement) -> str:
        text = convert_to_rst(node.get("children", [{}])[0], segments)
        separator = node.get('properties').get("separator", "-")
        level = separator * len(text)
        header_type = node.get('properties').get('header_type')

        if header_type == 'section':
            return f"{text}\n{level}\n"
        else:
            return f"{level}\n{text}\n{level}\n"
    
    def convert_comment(node: LayoutElement) -> str:
        text = convert_to_rst(node.get("children", [{}])[0], segments)
        separator = node.get('properties').get("separator", "..")
        return f"\n{separator}{text}\n"

    def convert_p(node: LayoutElement) -> str:
        children = [convert_to_rst(child, segments) for child in node.get("children", [])]
        return replace_tags("\n".join(children), node["properties"]) + "\n"

    def convert_section(node: LayoutElement) -> str:
        children = [convert_to_rst(child, segments) for child in node.get("children", [])]
        return "\n".join(children)

    def convert_ul(node: LayoutElement) -> str:
        items = [convert_to_rst(child, segments) for child in node.get("children", [])]
        return "\n".join(items)

    def convert_li(node: LayoutElement) -> str:
        children = [convert_to_rst(child, segments) for child in node.get("children", [])]
        separator = node.get('properties').get("separator", "-")
        return separator + " " + "\n  ".join(children)

    def convert_pre(node: LayoutElement) -> str:
        if node.get("children"):
            return "::\n\n  " + convert_to_rst(node["children"][0], segments)
        else:
            return "::\n\n"

    def convert_field_list(node: LayoutElement) -> str:
        items = [convert_to_rst(child, segments) for child in node.get("children", [])]
        return "\n\n".join(items)

    def convert_field(node: LayoutElement) -> str:
        name = convert_to_rst(node.get('children', [{}])[0], segments)
        body = convert_to_rst(node.get('children', [{}])[1], segments)
        return f"{name}:\n  {body}"

    def convert_system_message(node: LayoutElement) -> str:
        return convert_to_rst(node.get("children", [{}])[0], segments)
    
    def convert_table(node: LayoutElement) -> str:
        list_table = node.get('properties').get("list_table", "")
        
        if list_table != None:
            children = [convert_to_rst(child, segments) for child in node.get("children", [])]
            return list_table + "\n" + "".join(children)

        else:
            def get_table_dimensions(table_node):
                max_cols = 0
                rows = []

                for tgroup in table_node['children']:
                    for tbody in tgroup['children']:
                        if tbody['tagName'] in ['thead', 'tbody']:
                            rows.extend(tbody['children'])

                max_rows = len(rows)
                for row in rows:
                    col_count = 0
                    for entry in row['children']:
                        morecols = int(entry['properties'].get('morecols', 0))
                        col_count += 1 + morecols
                    max_cols = max(max_cols, col_count)
                
                return max_rows, max_cols

            def build_table_array(table_node, rows, cols):
                table_array = [['' for _ in range(cols)] for _ in range(rows)]
                row_idx = 0
                
                for tgroup in table_node['children']:
                    for tbody in tgroup['children']:
                        if tbody['tagName'] in ['thead', 'tbody']:
                            for row in tbody['children']:
                                col_idx = 0
                                for entry in row['children']:
                                    while table_array[row_idx][col_idx] != '':
                                        col_idx += 1
                                    cell_text = convert_entry_Table(entry)
                                    morecols = int(entry['properties'].get('morecols', 0))
                                    morerows = int(entry['properties'].get('morerows', 0))
                                    for i in range(morerows + 1):
                                        for j in range(morecols + 1):
                                            if i == 0 and j == 0:
                                                table_array[row_idx + i][col_idx + j] = cell_text
                                    col_idx += morecols + 1
                                row_idx += 1
                
                return table_array

            def restore_table(table_node):            
                max_rows, max_cols = get_table_dimensions(table_node)
                table_array = build_table_array(table_node, max_rows, max_cols)
                
                col_widths = [max(len(cell) for cell in col) for col in zip(*table_array)]
                
                def build_separator(char, widths):
                    return '+' + '+'.join([char * (w + 2) for w in widths]) + '+'
                
                horizontal_sep = build_separator('-', col_widths)
                header_sep = build_separator('=', col_widths)
                
                table_lines = []
                
                table_lines.append(horizontal_sep)
                
                for i, row in enumerate(table_array):
                    line = '| ' + ' | '.join(f"{cell:<{col_widths[j]}}" for j, cell in enumerate(row)) + ' |'
                    table_lines.append(line)
                    if i == 0:
                        table_lines.append(header_sep)
                    else:
                        table_lines.append(horizontal_sep)
                            
                return '\n'.join(table_lines)

            return restore_table(node)
        
    def convert_tgroup(node: LayoutElement) -> str:
        children = [convert_to_rst(child, segments) for child in node.get("children", [])]
        return "".join(children)
    
    def convert_thead(node: LayoutElement) -> str:
        children = [convert_to_rst(child, segments) for child in node.get("children", [])]
        return "\n".join(children)
    
    def convert_tbody(node: LayoutElement) -> str:
        children = [convert_to_rst(child, segments) for child in node.get("children", [])]
        return "".join(children)
    
    def convert_row(node: LayoutElement) -> str:
        children = [convert_to_rst(child, segments) for child in node.get("children", [])]
        return "   * - " + "     - ".join(children)
    
    def convert_entry(node: LayoutElement) -> str:
        children = [convert_to_rst(child, segments) for child in node.get("children", [])]
        return "\n".join(children)
    
    def convert_entry_Table(node: LayoutElement) -> str:
        children = [convert_to_rst(child, segments) for child in node.get("children", [])]
        return "".join(children).replace('\n', ' ').strip()
    
    def convert_target(node: LayoutElement) -> str:
        children = [convert_to_rst(child, segments) for child in node.get("children", [])]
        return "\n".join(children) + "\n"
    
    def convert_important(node: LayoutElement) -> str:
        children = [convert_to_rst(child, segments) for child in node.get("children", [])]
        return ".. important:: " + "\n".join(children) + "\n"
    
    def convert_note(node: LayoutElement) -> str:
        children = [convert_to_rst(child, segments) for child in node.get("children", [])]
        return ".. note:: " + "\n".join(children) + "\n"

    handlers = {
        "root": convert_root,
        "element": convert_element,
        "text": convert_text,
        "segment": convert_segment,
    }

    if node_type in handlers:
        return handlers[node_type](node)
    else:
        return ""





def strong(tag: str, content: str, properties: Dict[str, Callable[[str], str]]) -> str:
    separator = properties[tag]['separator']

    return f"{separator}{content}{separator}"

def reference(tag: str, content: str, properties: Dict[str, Callable[[str], str]]) -> str:
    url = properties[tag]['href']

    return f"`{content} {url}`__"

def literal(tag: str, content: str, properties: Dict[str, Callable[[str], str]]) -> str:
    return f"``{content}``"

def emphasis(tag: str, content: str, properties: Dict[str, Callable[[str], str]]) -> str:
    return f"*{content}*"

tag_config = {
    'strong': strong,
    'reference': reference,
    'literal': literal,
    'emphasis': emphasis
}

def replace_tags(input_string: str, properties: Dict[str, Callable[[str], str]]) -> str:
    pattern = r'\{(\w+)\}([^}]+)\{/\1\}'
    
    def replace(match: re.Match) -> str:
        tag_with_digits, content = match.groups()

        tag = ''.join(filter(str.isalpha, tag_with_digits))

        if tag in tag_config:

            text = tag_config[tag](tag_with_digits, content, properties)

            return text
        
        return content
    
    result = re.sub(pattern, replace, input_string)
    return result