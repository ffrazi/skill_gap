import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
from PIL import Image
import pytesseract

app = Flask(__name__)
CORS(app)

# Ensure the user has Tesseract installed and configured.
# On Windows, you might need to set the path explicitly:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Pre-defined list of skills to search for
SKILLS_DB = [
    'Python', 'Java', 'C++', 'C#', 'JavaScript', 'TypeScript', 'HTML', 'CSS', 'SQL', 'NoSQL',
    'React', 'Angular', 'Vue.js', 'Node.js', 'Express.js', 'Django', 'Flask', 'Spring Boot',
    'Ruby on Rails', 'ASP.NET', 'PHP', 'Laravel',
    'Git', 'Docker', 'Kubernetes', 'Jenkins', 'CI/CD', 'Agile', 'Scrum',
    'AWS', 'Azure', 'Google Cloud Platform (GCP)',
    'TensorFlow', 'PyTorch', 'scikit-learn', 'Pandas', 'NumPy', 'Machine Learning', 'Deep Learning',
    'Data Analysis', 'Data Visualization', 'Natural Language Processing (NLP)',
    'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'SQLite',
    'Linux', 'Unix', 'Windows Server', 'Cybersecurity', 'Network Security'
]

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = "".join(page.get_text() for page in doc)
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_image(image_path):
    try:
        return pytesseract.image_to_string(Image.open(image_path))
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""

def extract_skills(text, skills_db):
    """Extracts skills from text by matching against a predefined skill list."""
    found_skills = set()
    for skill in skills_db:
        # Use word boundaries and case-insensitive matching
        if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
            found_skills.add(skill)
    return list(found_skills)

@app.route('/api/analyze', methods=['POST'])
def analyze_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file provided'}), 400

    resume_file = request.files['resume']
    jd_text = request.form.get('jd', '')

    if not resume_file or resume_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = resume_file.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    resume_file.save(file_path)

    resume_text = ""
    if filename.lower().endswith('.pdf'):
        resume_text = extract_text_from_pdf(file_path)
    elif filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        resume_text = extract_text_from_image(file_path)
    else:
        os.remove(file_path)
        return jsonify({'error': 'Unsupported file type. Please upload a PDF, PNG, or JPG file.'}), 400

    if not resume_text:
        os.remove(file_path)
        return jsonify({'error': 'Could not extract text from the resume.'}), 500
        
    if not jd_text:
        return jsonify({'error': 'No job description provided'}), 400

    # Clean up the uploaded file
    os.remove(file_path)

    # Extract skills from resume and job description
    resume_skills = extract_skills(resume_text, SKILLS_DB)
    jd_skills = extract_skills(jd_text, SKILLS_DB)

    # Perform gap analysis to find missing skills
    missing_skills = list(set(jd_skills) - set(resume_skills))

    # Generate recommendations (placeholder)
    recommendations = [
        {"title": f"Course for {skill}", "url": f"https://www.google.com/search?q=online+course+for+{skill.replace(' ', '+')}"}
        for skill in missing_skills
    ]

    return jsonify({
        'resume_skills': sorted(resume_skills),
        'jd_skills': sorted(jd_skills),
        'missing_skills': sorted(missing_skills),
        'recommendations': recommendations,
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
