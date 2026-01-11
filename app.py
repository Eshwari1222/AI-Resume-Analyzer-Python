

# from flask import Flask, render_template, request
# import pdfplumber
# from PyPDF2 import PdfReader
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity

# app = Flask(__name__)

# # ---------------- PDF TEXT EXTRACTION (SAFE) ----------------
# def extract_text_from_pdf(file):
#     text = ""

#     try:
#         with pdfplumber.open(file) as pdf:
#             for page in pdf.pages:
#                 if page.extract_text():
#                     text += page.extract_text()

#         if not text.strip():
#             file.seek(0)
#             reader = PdfReader(file)
#             for page in reader.pages:
#                 text += page.extract_text() or ""

#     except Exception as e:
#         print("PDF Error:", e)
#         return None

#     return text


# # ---------------- SKILL MATCHING ----------------
# def calculate_match(resume_text, job_text):
#     vectorizer = TfidfVectorizer(stop_words="english")
#     vectors = vectorizer.fit_transform([resume_text, job_text])
#     score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
#     return round(score * 100, 2)


# # ---------------- ROUTES ----------------
# @app.route("/", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         resume = request.files.get("resume")
#         job = request.form.get("job")

#         if not resume or resume.filename == "":
#             return render_template("index.html", error="📄 Please upload a PDF resume")

#         if not resume.filename.lower().endswith(".pdf"):
#             return render_template("index.html", error="❌ Only PDF files are allowed")

#         resume_text = extract_text_from_pdf(resume)

#         if not resume_text:
#             return render_template(
#                 "index.html",
#                 error="⚠️ Unable to read this PDF. Please upload a text-based resume."
#             )

#         job_descriptions = {
#             "Data Scientist": "python machine learning pandas numpy statistics data analysis",
#             "AI Engineer": "deep learning neural networks tensorflow pytorch ai",
#             "Web Developer": "html css javascript flask backend frontend"
#         }

#         job_text = job_descriptions.get(job, job)

#         score = calculate_match(resume_text, job_text)

#         resume_words = set(resume_text.lower().split())
#         job_words = set(job_text.lower().split())
#         missing_skills = list(job_words - resume_words)

#         return render_template(
#             "result.html",
#             job=job,
#             score=score,
#             missing_skills=missing_skills[:8]
#         )

#     return render_template("index.html")


# if __name__ == "__main__":
#     app.run(debug=True)


from flask import Flask, render_template, request
import PyPDF2
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# SKILLS = {
#     "data scientist": ["python", "machine learning", "pandas", "numpy", "statistics"],
#     "web developer": ["html", "css", "javascript", "flask", "react"],
#     "ai engineer": ["python", "deep learning", "nlp", "tensorflow", "pytorch"],
#     "Full Stack Developer": ["html", "css", "javascript", "node.js", "react", "database"],

# }
SKILLS = {
    "data scientist": [
        "python", "machine learning", "pandas", "numpy", "statistics"
    ],
    "web developer": [
        "html", "css", "javascript", "flask", "react"
    ],
    "ai engineer": [
        "python", "deep learning", "nlp", "tensorflow", "pytorch"
    ],
    "full stack developer": [
        "html", "css", "javascript", "python", "flask",
        "react", "sql", "mongodb", "api", "git"
    ]
}


def extract_text_from_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.lower()
    except:
        return ""

def calculate_similarity(resume_text, job_skills):
    docs = [resume_text, " ".join(job_skills)]
    tfidf = TfidfVectorizer()
    matrix = tfidf.fit_transform(docs)
    score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
    return round(score * 100, 2)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        job_role = request.form["job"]
        resume = request.files["resume"]

        resume_text = extract_text_from_pdf(resume)

        job_skills = SKILLS[job_role]
        score = calculate_similarity(resume_text, job_skills)

        missing_skills = [s for s in job_skills if s not in resume_text]

        if score >= 80:
            verdict = "Excellent Match 🎯"
        elif score >= 60:
            verdict = "Good Match 👍"
        else:
            verdict = "Needs Improvement ⚠️"

        summary = f"Your resume matches {score}% with the {job_role.title()} role based on AI skill similarity analysis."

        return render_template(
            "result.html",
            score=score,
            verdict=verdict,
            summary=summary,
            job=job_role.title(),
            missing_skills=missing_skills
        )

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

