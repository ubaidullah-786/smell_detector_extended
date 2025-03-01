import ast
import os
from flask import Flask

app = Flask(__name__)

# Code smell detection functions
def detect_large_class(node):
    if isinstance(node, ast.ClassDef):
        loc = len(node.body)  # Lines of code based on the number of nodes
        attributes = sum(isinstance(n, ast.Assign) for n in node.body)  # Attribute assignments
        methods = sum(isinstance(n, ast.FunctionDef) for n in node.body)  # Method definitions
        if loc >= 200 or attributes + methods > 40:
            return "Large Class"
    return None

def detect_long_parameter_list(node):
    if isinstance(node, ast.FunctionDef):
        if len(node.args.args) >= 5:
            return "Long Parameter List"
    return None

def detect_long_method(node):
    if isinstance(node, ast.FunctionDef):
        method_loc = len(node.body)  # Number of nodes in the method body
        if method_loc >= 100:
            return "Long Method"
    return None

def detect_long_message_chain(node):
    if isinstance(node, ast.Expr):
        chain_length = 0
        current = node.value
        while isinstance(current, ast.Attribute):  # Traverse attribute chain
            chain_length += 1
            current = current.value
        if chain_length >= 4:
            return "Long Message Chain"
    return None

def detect_long_base_class_list(node):
    if isinstance(node, ast.ClassDef):
        if len(node.bases) >= 3:  # Number of base classes
            return "Long Base Class List"
    return None

def detect_long_lambda_function(node):
    if isinstance(node, ast.Lambda):
        lambda_chars = len(ast.dump(node))  # Character count in lambda
        if lambda_chars >= 80:
            return "Long Lambda Function"
    return None

def detect_long_element_chain(node):
    if isinstance(node, ast.Call):
        chain_length = 0
        current = node.func
        while isinstance(current, ast.Attribute):  # Count chained calls like `obj.attr1.attr2()`
            chain_length += 1
            current = current.value
        if chain_length >= 3:
            return "Long Element Chain"
    return None

def detect_long_ternary_conditional_expression(node):
    if isinstance(node, ast.IfExp):  # Matches ternary expression (a if cond else b)
        expr_length = len(ast.dump(node))  # Character count in the expression
        if expr_length >= 40:
            return "Long Ternary Conditional Expression"
    return None

def analyze_code(file_path):
    results = {}  # Dictionary to store smells and their line numbers
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.readlines()  # Read entire file content
        tree = ast.parse("".join(file_content))
    except (UnicodeDecodeError, SyntaxError):
        return {}  # Return empty results if the file can't be parsed

    detectors = [
        detect_large_class,
        detect_long_parameter_list,
        detect_long_method,
        detect_long_message_chain,
        detect_long_base_class_list,
        detect_long_lambda_function,
        detect_long_element_chain,
        detect_long_ternary_conditional_expression,
    ]

    for node in ast.walk(tree):
        for detector in detectors:
            smell = detector(node)
            if smell:
                if smell not in results:
                    results[smell] = {"lines": [], "file_content": file_content}
                results[smell]["lines"].append(node.lineno)

    return results

def traverse_directory(root_folder):
    detected_smells = {}
    for root, _, files in os.walk(root_folder):
        for file in files:
            if file.endswith('.py'):  # Only analyze Python files
                file_path = os.path.join(root, file)
                smells = analyze_code(file_path)
                if smells:
                    detected_smells[file_path] = smells
    return detected_smells
