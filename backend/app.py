import os
import shutil
from flask import Flask, request, jsonify
from flask_cors import CORS
from smell_detector import traverse_directory

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploaded_projects"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/upload", methods=["POST"])
def upload_project():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filename = file.filename
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    file.save(file_path)

    if filename.endswith(".zip"):
        project_folder = os.path.join(
            app.config["UPLOAD_FOLDER"], filename.replace(".zip", "")
        )
        shutil.unpack_archive(file_path, project_folder)
        os.remove(file_path)
    else:
        project_folder = os.path.join(app.config["UPLOAD_FOLDER"], os.path.splitext(filename)[0])
        os.makedirs(project_folder, exist_ok=True)
        shutil.unpack_archive(file_path, project_folder)

    detected_smells = traverse_directory(project_folder)

    smells_summary = {}
    total_smells = 0
    for file_path, smells in detected_smells.items():
        for smell_type, data in smells.items():
            if smell_type not in smells_summary:
                smells_summary[smell_type] = []
            smells_summary[smell_type].append({
                "file": file_path,
                "lines": data["lines"],
                "file_content": data["file_content"],
                "full_code": data["full_code"] if "full_code" in data else [],
                "range": data["range"] if "range" in data else {"start": None, "end": None}
            })
            total_smells += len(data["lines"])

    shutil.rmtree(project_folder)

    return jsonify(
        {
            "total_smells": total_smells,
            "smell_breakdown": smells_summary,
        }
    )

if __name__ == "__main__":
    app.run(debug=True)
