import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)

# Set up upload folder
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

def fetch_jobs_from_api(location="Remote", experience="Any", job_type="Any"):
    """Fetch jobs from Arbeitnow API with minimal filtering."""
    url = "https://arbeitnow.com/api/job-board-api"  # No filters to ensure we get jobs
    try:
        response = requests.get(url, timeout=10)
        print(f"API Response Status: {response.status_code}")
        if response.status_code == 200:
            jobs = response.json().get("data", [])
            print(f"Fetched {len(jobs)} jobs from API.")
            if not jobs:
                print("API returned no jobs.")
                return [{"title": "Sample Job 1", "company_name": "Test Co", "description": "Python skills needed", "url": "#"}]
            # Take first 50 jobs, no strict filtering
            return [
                {"title": job["title"], "company_name": job["company_name"], "description": job["description"], "url": job.get("url", "#")}
                for job in jobs[:50]
            ]
        else:
            print(f"API failed with status: {response.status_code}, text: {response.text}")
            return [{"title": "Sample Job 2", "company_name": "Fallback Inc", "description": "Generic job", "url": "#"}]
    except requests.RequestException as e:
        print(f"API fetch error: {e}")
        return [{"title": "Sample Job 3", "company_name": "Error Co", "description": "Fallback job", "url": "#"}]

def extract_text_from_file(file_path):
    """Extract text from PDF, DOCX, or TXT files."""
    try:
        if file_path.endswith(".pdf"):
            reader = PdfReader(file_path)
            text = " ".join([page.extract_text() or "" for page in reader.pages])
        elif file_path.endswith(".docx"):
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
        elif file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            print(f"Unsupported file format: {file_path}")
            return "Unsupported file format"
        text = text.strip()
        print(f"Extracted text (first 100 chars): {text[:100] or 'No text extracted'}...")
        return text if text else "No text found in file"
    except Exception as e:
        print(f"Text extraction error: {e}")
        return "Error extracting text"

def match_jobs(resume_text, jobs):
    """Match resume to jobs using TF-IDF."""
    if not jobs or not resume_text.strip():
        print("No jobs or resume text to match.")
        return [{"title": "No jobs available", "company": "N/A", "score": 0.0, "url": "#"}]
    
    job_descriptions = [job["description"] for job in jobs]
    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_text] + job_descriptions)
        similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        print(f"Similarity scores: {similarity_scores[:5]}... (first 5)")
        ranked_jobs = sorted(zip(jobs, similarity_scores), key=lambda x: x[1], reverse=True)
        return [
            {"title": job["title"], "company": job["company_name"], "score": round(score * 100, 2), "url": job["url"]}
            for job, score in ranked_jobs[:10]  # Limit to top 10
        ]
    except Exception as e:
        print(f"Matching error: {e}")
        return [{"title": "Matching error", "company": "N/A", "score": 0.0, "url": "#"}]

@app.route("/upload-resume", methods=["POST"])
def upload_resume():
    """Process resume and return job matches."""
    print("Received upload request.")
    if "resume" not in request.files:
        print("No file uploaded.")
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["resume"]
    if not file.filename:
        print("No file selected.")
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)
    print(f"Saved file: {filepath}")

    resume_text = extract_text_from_file(filepath)
    if "Error" in resume_text or "Unsupported" in resume_text or not resume_text.strip():
        print(f"Resume text issue: {resume_text}")
        return jsonify({"error": resume_text}), 400

    jobs = fetch_jobs_from_api()  # No filters for max results
    job_matches = match_jobs(resume_text, jobs)
    print(f"Returning {len(job_matches)} job matches.")
    return jsonify({"job_recommendations": job_matches})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)