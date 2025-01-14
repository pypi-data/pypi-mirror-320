from docutils.core import publish_doctree
from typing import List
from localizesh_sdk import Context, Document, LayoutRoot, Processor, Segment, IdGenerator
from .utils.post_parse_doctree import post_parse_doctree
from .utils.convert_to_ast import convert_to_ast
from .utils.convert_to_rst import convert_to_rst


class RstProcessor(Processor):
    
    def parse(self, res: str, ctx: Context) -> Document:
        generator = IdGenerator()
        doctree = publish_doctree(res)
        doctree = post_parse_doctree(res, doctree)
        ast = convert_to_ast(doctree)
        segments: List[Segment] = []

        def replace_text_with_segment(node):
            if node and node.get("type") == "text":
                text = node["value"]
                tags = node.get("tags", None)
                
                segment_id = generator.generate_id(text=text, tags=tags, context=str(ctx))
                segment = {"id": segment_id, "text": text}
                
                if tags:
                    segment["tags"] = tags
                
                segments.append(segment)
                
                return {"type": "segment", "id": segment_id}
            
            elif node and "children" in node:
                node["children"] = [replace_text_with_segment(child) for child in node["children"]]
            
            return node

        layout: LayoutRoot = replace_text_with_segment(ast)

        return Document(layout=layout, segments=segments)
    

    def stringify(self, document: Document, ctx: Context) -> str:
        return convert_to_rst(document.layout, document.segments)