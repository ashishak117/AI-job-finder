import os
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from docx import Document
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///job_recommendation.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

def authenticate():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        abort(401, description="Authentication required")
    
    user = User.query.filter_by(email=auth.username.lower()).first()
    if not user or not check_password_hash(user.password, auth.password):
        abort(401, description="Invalid credentials")
    return user

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email", "").lower()
    password = data.get("password", "").strip()

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password=hashed_password)

    try:
        db.session.add(new_user)
        db.session.commit()
        user = User.query.filter_by(email=email).first()
        if user:
            print(f"User registered: {email}, ID: {user.id}")
        else:
            print("Failed to find user after commit")
        return jsonify({"message": "User registered successfully"}), 201
    except:
        db.session.rollback()
        print(f"Registration failed: Email {email} already exists")
        return jsonify({"error": "Email already exists"}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email", "").lower()
    password = data.get("password", "").strip()

    if not password:
        print("Password is missing or empty")
        return jsonify({"error": "Password is required"}), 400

    print(f"Login attempt for email: {email}")
    user = User.query.filter_by(email=email).first()
    if not user:
        print(f"No user found for email: {email}")
        return jsonify({"error": "Invalid credentials"}), 401
    if not check_password_hash(user.password, password):
        print(f"Password mismatch for email: {email}")
        return jsonify({"error": "Invalid credentials"}), 401

    print(f"Login successful for email: {email}")
    return jsonify({"message": "Login successful"}), 200

def fetch_jobs_from_api():
    url = "https://arbeitnow.com/api/job-board-api"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            jobs = response.json().get("data", [])[:50]
            return jobs if jobs else []
    except requests.RequestException:
        return []
    return []

def extract_text_from_file(file_path):
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
            return "Unsupported file format"
        return text.strip() if text.strip() else "No text found"
    except:
        return "Error extracting text"

def match_jobs(resume_text, jobs):
    if not jobs or not resume_text.strip():
        return [{"title": "No jobs available", "company": "N/A", "score": 0.0, "url": "#"}]

    # Prepare documents: resume + job descriptions
    job_descriptions = [job["description"] for job in jobs]
    documents = [resume_text] + job_descriptions

    # Use TF-IDF Vectorizer with stop words removal
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    try:
        tfidf_matrix = vectorizer.fit_transform(documents)
        # Calculate cosine similarity between resume (first row) and jobs (remaining rows)
        similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

        # Pair jobs with their similarity scores and sort
        ranked_jobs = sorted(
            zip(jobs, similarity_scores),
            key=lambda x: x[1],
            reverse=True
        )

        # Return top 10 matches with scores as percentages
        matched_jobs = [
            {
                "title": job["title"],
                "company": job["company_name"],
                "score": round(score * 100, 2),  # Convert to percentage
                "url": job["url"]
            }
            for job, score in ranked_jobs[:10]
            if score > 0.05  # Threshold to filter low relevance (adjustable)
        ]

        return matched_jobs or [
            {"title": "No good matches", "company": "N/A", "score": 0.0, "url": "#"}
        ]
    except Exception as e:
        print(f"Error in job matching: {str(e)}")
        return [{"title": "Matching error", "company": "N/A", "score": 0.0, "url": "#"}]

@app.route("/upload-resume", methods=["POST"])
def upload_resume():
    user = authenticate()

    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["resume"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    resume_text = extract_text_from_file(filepath)
    if "Error" in resume_text or "Unsupported" in resume_text or not resume_text.strip():
        return jsonify({"error": resume_text}), 400

    jobs = fetch_jobs_from_api()
    job_matches = match_jobs(resume_text, jobs)

    return jsonify({"job_recommendations": job_matches})

if __name__ == "__main__":
    app.run(debug=True)