import sys
import json
import tree_sitter_cpp
from tree_sitter import Language, Parser

if len(sys.argv) < 2:
    sys.exit(1)

file_path = sys.argv[1]
with open(file_path, "r") as f:
    code_bytes = f.read().encode("utf-8")

CPP_LANGUAGE = Language(tree_sitter_cpp.language())
parser = Parser(CPP_LANGUAGE)
tree = parser.parse(code_bytes)

nodes = []
edges = []
node_count = 0

function_directory = {}
calls_to_link = []
injections = [] 

def add_node(label, node_type, description="", parent_id=None):
    global node_count
    n_id = f"node_{node_count}"
    
    nodes.append({
        "id": n_id,
        "type": "customNode",
        "data": { "label": label, "type": node_type, "description": description },
        "position": { "x": 0, "y": 0 }
    })
    
    node_count += 1
    
    if parent_id:
        edges.append({ "id": f"e_{parent_id}_{n_id}", "source": parent_id, "target": n_id, "animated": True, "type": "smoothstep", "style": { "stroke": "#38bdf8", "strokeWidth": 2 } })
        
    return n_id

def queue_injection(node, n_id):
    body = next((c for c in node.children if c.type == "compound_statement"), None)
    if body and len(body.children) > 0 and body.children[0].type == "{":
        injections.append((body.children[0].end_byte, f"\n    telemetry_ping(\"{n_id}\");"))

def traverse(node, parent_id=None):
    current_id = parent_id
    
    if node.type == "function_definition":
        decl = next((n for n in node.children if n.type == "function_declarator"), None)
        if decl:
            ident = next((n for n in decl.children if n.type == "identifier"), None)
            if ident:
                name = code_bytes[ident.start_byte:ident.end_byte].decode("utf-8")
                current_id = add_node(f"{name}()", "function", "Function Definition", parent_id)
                function_directory[name] = current_id
                queue_injection(node, current_id)
                    
    elif node.type == "declaration":
        ident = None
        for n in node.children:
            if n.type == "init_declarator":
                ident = next((c for c in n.children if c.type == "identifier"), None)
                break
            elif n.type == "identifier":
                ident = n
        if ident:
            name = code_bytes[ident.start_byte:ident.end_byte].decode("utf-8")
            current_id = add_node(name, "variable", "Variable Decl", parent_id)
            
    elif node.type == "if_statement":
        current_id = add_node("if (...)", "condition", "Branch logic", parent_id)
        cons = next((c for c in node.children if c.type == "compound_statement"), None)
        if cons and len(cons.children) > 0 and cons.children[0].type == "{":
            injections.append((cons.children[0].end_byte, f"\n    telemetry_ping(\"{current_id}\");"))
        
    elif node.type in ("for_statement", "while_statement"):
        current_id = add_node("Loop", "loop", node.type, parent_id)
        queue_injection(node, current_id)
        
    elif node.type == "call_expression":
        func = node.children[0]
        name = code_bytes[func.start_byte:func.end_byte].decode("utf-8")
        current_id = add_node(f"Call: {name}()", "code", "Execution Call", parent_id)
        calls_to_link.append((current_id, name))

    for child in node.children:
        traverse(child, current_id)

traverse(tree.root_node)

for call_node_id, func_name in calls_to_link:
    if func_name in function_directory:
        edges.append({ "id": f"e_jump_{call_node_id}_{function_directory[func_name]}", "source": call_node_id, "target": function_directory[func_name], "animated": True, "type": "smoothstep", "label": "JUMPS TO", "style": { "stroke": "#ef4444", "strokeWidth": 3, "strokeDasharray": "5 5" } })

out_file = "/home/integrity/Desktop/agent/01_Projects/architecture-visualizer/architecture.json"
with open(out_file, "w") as f:
    json.dump({"nodes": nodes, "edges": edges}, f, indent=2)

injections.sort(key=lambda x: x[0], reverse=True)
traced_bytes = code_bytes
for idx, text in injections:
    traced_bytes = traced_bytes[:idx] + text.encode("utf-8") + traced_bytes[idx:]

traced_code = "#include \"telemetry.h\"\n\n" + traced_bytes.decode("utf-8")
traced_file = file_path.replace(".cpp", "_traced.cpp")

with open(traced_file, "w") as f:
    f.write(traced_code)

print(f"Parsed {node_count} nodes.")
print(f"Injected {len(injections)} telemetry hooks!")
