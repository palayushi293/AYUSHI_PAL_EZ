# app.py
from flask import Flask, render_template, request, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv # type: ignore
#from utils.extract import extract_text # type#: ignore
#from utils.qa import answer_question, generate_logic_questions, evaluate_answer # type: ignore

# Load environment variables
load_dotenv("enviro.env")


app = Flask(__name__)
app.secret_key = 'anything_for_dev_mode'


app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API"))

def answer_question(context, question):
    prompt = f"""You are an intelligent assistant. Answer the question based only on the following document.

Document:
{context}

Question: {question}
Answer:"""
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def generate_logic_questions(context):
    prompt = f"""Generate 3 logic or comprehension-based questions from the document below. List them as:
1.
2.
3.

Document:
{context}"""
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def evaluate_answer(context, question, user_answer):
    prompt = f"""Evaluate the user's answer to the question based on the document below.

Document:
{context}

Question: {question}
User's Answer: {user_answer}

Evaluation:"""
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


# File type checker
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


import fitz  # type: ignore # PyMuPDF for PDF reading

def extract_text(filepath, file_type):
    if file_type == 'pdf':
        text = ""
        with fitz.open(filepath) as doc:
            for page in doc:
                text += page.get_text()
        return text.strip()
    elif file_type == 'txt':
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return ""



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            file_type = filename.rsplit('.', 1)[1].lower()
            text = extract_text(filepath, file_type) # type: ignore
            summary = text[:150] + "..." if len(text) > 150 else text

            session['document_text'] = text
            session['summary'] = summary

            os.remove(filepath)

            return redirect(url_for('interaction'))

    return render_template('index.html')

@app.route('/interaction')
def interaction():
    return render_template('interaction.html', summary=session.get('summary'))

@app.route('/ask', methods=['GET', 'POST'])
def ask():
    answer = None
    if request.method == 'POST':
        question = request.form['question']
        answer = answer_question(session['document_text'], question) # type: ignore
    return render_template('ask.html', answer=answer)

@app.route('/challenge', methods=['GET', 'POST'])
def challenge():
    if request.method == 'GET':
        questions = generate_logic_questions(session['document_text']) # type: ignore
        session['questions'] = questions.split('\n')[:3]
        return render_template('challenge.html', questions=session['questions'])
    else:
        user_answers = [request.form.get(f'answer{i}') for i in range(3)]
        evaluations = [
            evaluate_answer(session['document_text'], session['questions'][i], user_answers[i]) # type: ignore
            for i in range(3)
        ]
        return render_template('res.html', evaluations=evaluations)
@app.route('/summary_logic')
def summary_logic():
    context = session.get('document_text')
    if not context:
        return redirect(url_for('index'))

    # Generate summary
    summary_prompt = f"""Summarize the following document in 5-7 lines:

Document:
{context}
"""
    summary_response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": summary_prompt}]
    )
    summary = summary_response.choices[0].message.content.strip()

    logic_prompt = f"""Based on the following summary, generate 2 or 3 logic or comprehension-based questions.

Summary:
{summary}
"""
    logic_response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": logic_prompt}]
    )
    questions = logic_response.choices[0].message.content.strip().split("\n")

    return render_template("summary_logic.html", summary=summary, questions=questions)




if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
