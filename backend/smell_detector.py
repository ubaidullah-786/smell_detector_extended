import ast
import os
import zipfile
import tempfile
from flask import Flask, request, jsonify

app = Flask(__name__)

# Code smell detection functions
def detect_large_class(node):
    if isinstance(node, ast.ClassDef):
        loc = len(node.body)
        attributes = sum(isinstance(n, ast.Assign) for n in node.body)
        methods = sum(isinstance(n, ast.FunctionDef) for n in node.body)
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
        method_loc = len(node.body)
        if method_loc >= 100:
            return "Long Method"
    return None

def detect_long_message_chain(node):
    if isinstance(node, ast.Expr):
        chain_length = 0
        current = node.value
        while isinstance(current, ast.Attribute):
            chain_length += 1
            current = current.value
        if chain_length >= 4:
            return "Long Message Chain"
    return None

def detect_long_base_class_list(node):
    if isinstance(node, ast.ClassDef):
        if len(node.bases) >= 3:
            return "Long Base Class List"
    return None

def detect_long_lambda_function(node):
    if isinstance(node, ast.Lambda):
        lambda_chars = len(ast.dump(node))
        if lambda_chars >= 80:
            return "Long Lambda Function"
    return None

def analyze_code(file_path):
    # Add a dictionary to store smells with line numbers
    results = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            code = file.read()
        tree = ast.parse(code)
    except (UnicodeDecodeError, SyntaxError):
        return {}

    for node in ast.walk(tree):
        smell = detect_large_class(node)
        if smell:
            results.setdefault(smell, []).append(node.lineno)
        # Repeat the same for each smell detector
        for detector in [detect_long_parameter_list, detect_long_method, 
                          detect_long_message_chain, detect_long_base_class_list, 
                          detect_long_lambda_function]:
            smell = detector(node)
            if smell:
                results.setdefault(smell, []).append(node.lineno)
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


# Flask API to handle uploads
@app.route('/upload', methods=['POST'])
def upload_and_analyze():
    # Ensure a file is uploaded
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Ensure the uploaded file is a zip file
    if not file.filename.endswith('.zip'):
        return jsonify({"error": "Uploaded file must be a .zip"}), 400

    # Create a temporary directory to extract the zip file
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, file.filename)
        file.save(zip_path)

        # Extract the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Traverse the extracted directory and analyze Python files
        detected_smells = traverse_directory(temp_dir)

        # Count total smells
        total_smells = sum(len(smells) for smells in detected_smells.values())

        return jsonify({
            "total_smells": total_smells,
            "smell_breakdown": {
                os.path.relpath(file, temp_dir): smells
                for file, smells in detected_smells.items()
            }
        })

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
