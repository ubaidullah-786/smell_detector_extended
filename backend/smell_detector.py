import ast
import os
from flask import Flask

app = Flask(__name__)

# Extract full class or method with range
def extract_full_code(node, file_content):
    """Extracts full class or function definition from the source file."""
    start_line = node.lineno - 1
    end_line = node.end_lineno if hasattr(node, "end_lineno") else start_line + 1
    return {
        "full_code": file_content[start_line:end_line],
        "range": {"start": start_line + 1, "end": end_line}
    }

# Code smell detection functions
def detect_large_class(node, file_content):
    if isinstance(node, ast.ClassDef):
        loc = len(node.body)
        attributes = sum(isinstance(n, ast.Assign) for n in node.body)
        methods = sum(isinstance(n, ast.FunctionDef) for n in node.body)
        if loc >= 200 or attributes + methods > 40:
            extracted = extract_full_code(node, file_content)
            return "Large Class", extracted
    return None, None

def detect_long_parameter_list(node, _):
    if isinstance(node, ast.FunctionDef):
        if len(node.args.args) >= 5:
            return "Long Parameter List", None
    return None, None

def detect_long_method(node, file_content):
    if isinstance(node, ast.FunctionDef):
        method_loc = len(node.body)
        if method_loc >= 100:
            extracted = extract_full_code(node, file_content)
            return "Long Method", extracted
    return None, None

def detect_long_message_chain(node, _):
    if isinstance(node, ast.Expr):
        chain_length = 0
        current = node.value
        while isinstance(current, ast.Attribute):
            chain_length += 1
            current = current.value
        if chain_length >= 4:
            return "Long Message Chain", None
    return None, None

def detect_long_base_class_list(node, file_content):
    if isinstance(node, ast.ClassDef):
        if len(node.bases) >= 3:
            extracted = extract_full_code(node, file_content)
            return "Long Base Class List", extracted
    return None, None

def detect_long_element_chain(node, _):
    if isinstance(node, ast.Call):
        chain_length = 0
        current = node.func
        while isinstance(current, ast.Attribute):
            chain_length += 1
            current = current.value
        if chain_length >= 3:
            return "Long Element Chain", None
    return None, None

def analyze_code(file_path):
    results = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.readlines()
        tree = ast.parse("".join(file_content))
    except (UnicodeDecodeError, SyntaxError):
        return {}

    detectors = [
        detect_large_class,
        detect_long_parameter_list,
        detect_long_method,
        detect_long_message_chain,
        detect_long_base_class_list,
        detect_long_element_chain,
    ]

    for node in ast.walk(tree):
        for detector in detectors:
            smell, extracted = detector(node, file_content)
            if smell:
                if smell not in results:
                    results[smell] = {
                        "lines": [],
                        "full_code": [],
                        "file_content": file_content,
                        "range": {"start": None, "end": None}
                    }
                results[smell]["lines"].append(node.lineno)
                if extracted:
                    results[smell]["full_code"].extend(extracted["full_code"])
                    results[smell]["range"] = extracted["range"]

    return results

def traverse_directory(root_folder):
    detected_smells = {}
    for root, _, files in os.walk(root_folder):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                smells = analyze_code(file_path)
                if smells:
                    detected_smells[file_path] = smells
    return detected_smells
