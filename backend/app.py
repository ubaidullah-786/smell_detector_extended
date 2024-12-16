import os
import shutil
from flask import Flask, request, jsonify
from flask_cors import CORS
from smell_detector import traverse_directory  # Import smell detection logic

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploaded_projects"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/upload", methods=["POST"])
def upload_project():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filename = file.filename

    # Define file paths
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    # Save the uploaded file
    file.save(file_path)

    # Determine if it's a zip or folder
    if filename.endswith(".zip"):
        # Extract zip files
        project_folder = os.path.join(
            app.config["UPLOAD_FOLDER"], filename.replace(".zip", "")
        )
        shutil.unpack_archive(file_path, project_folder)
        os.remove(file_path)  # Clean up the zip file
    else:
        # Save as a folder if not zipped
        project_folder = os.path.join(app.config["UPLOAD_FOLDER"], os.path.splitext(filename)[0])
        os.makedirs(project_folder, exist_ok=True)
        shutil.unpack_archive(file_path, project_folder)

    # Analyze smells in the extracted project folder
    detected_smells = traverse_directory(project_folder)

    # Summarize the results
    smells_summary = {}
    total_smells = 0
    for file_path, smells in detected_smells.items():
        for smell_type, lines in smells.items():
            if smell_type not in smells_summary:
                smells_summary[smell_type] = []
            smells_summary[smell_type].append({"file": file_path, "lines": lines})
            total_smells += len(lines)

    # Clean up the folder after analysis
    shutil.rmtree(project_folder)

    # Return the analysis results
    return jsonify(
        {
            "total_smells": total_smells,
            "smell_breakdown": smells_summary,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
