import os
import shutil
from flask import Flask, request, jsonify
from flask_cors import CORS
from smell_detector import traverse_directory  # Import your smell detection logic

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing (for React frontend)

UPLOAD_FOLDER = 'uploaded_projects'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_project():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename.split('.')[-1] != 'zip':
        return jsonify({"error": "Only .zip files are allowed"}), 400

    # Save the zip file
    zip_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(zip_path)

    # Extract the zip
    project_folder = os.path.join(app.config['UPLOAD_FOLDER'], file.filename.replace('.zip', ''))
    shutil.unpack_archive(zip_path, project_folder)
    os.remove(zip_path)

    # Detect smells in the extracted folder
    detected_smells = traverse_directory(project_folder)

    # Summarize results
    smells_summary = {}
    total_smells = 0
    for _, smells in detected_smells.items():
        total_smells += len(smells)
        for smell in smells:
            smells_summary[smell] = smells_summary.get(smell, 0) + 1

    # Return analysis to frontend
    return jsonify({
        "total_smells": total_smells,
        "smell_breakdown": smells_summary
    })

if __name__ == '__main__':
    app.run(debug=True)
