from flask import Flask, Blueprint, jsonify, request, render_template
import os
from pathlib import Path

app = Flask(__name__)
syllabus_bp = Blueprint('syllabus', __name__)

# Define the folders where syllabus and data are stored
SYLLABUS_FOLDER = Path('syllabus')
DATA_FOLDER = Path('data')


# Helper function to get chapters for a subject
def get_chapters(subject):
    subject_folder = SYLLABUS_FOLDER / subject.lower()  # Assuming subject folder names are lowercase
    if subject_folder.exists():
        # List all chapter directories
        chapters = [chapter.name for chapter in subject_folder.iterdir() if chapter.is_dir()]
        return chapters
    return []

def get_topics(subject, chapter):
    chapter_folder = SYLLABUS_FOLDER / subject.lower() / chapter  # Assuming chapter folder names are as provided
    if chapter_folder.exists():
        # List all topic directories under the selected chapter
        topics = [topic.name for topic in chapter_folder.iterdir() if topic.is_dir()]
        return topics
    return []

# Helper function to get questions from topics
def get_questions(subject, chapter, topics):
    questions = {}
    for topic in topics:
        topic_folder = DATA_FOLDER / subject.lower() / chapter  # Path to the topic folder
        topic_file = topic_folder / f"{topic}.excel"  # Assuming questions are in .txt files
        if topic_file.exists():
            with open(topic_file, 'r') as file:
                questions[topic] = file.readlines()
    return questions


# API endpoint to fetch chapters or topics
@syllabus_bp.route('/api/subjects/<subject>', methods=['GET'])
def api_subjects(subject):
    chapter = request.args.get('chapter')
    if chapter:
        topics = get_topics(subject, chapter)
        return jsonify({chapter: topics})
    else:
        chapters = get_chapters(subject)
        return jsonify({subject: chapters})


# API endpoint to fetch questions based on selected topics
@syllabus_bp.route('/api/questions', methods=['POST'])
def api_questions():
    data = request.json
    subject = data.get('subject')
    chapter = data.get('chapter')
    topics = data.get('topics', [])
    
    if subject and chapter and topics:
        questions = get_questions(subject, chapter, topics)
        return jsonify(questions)
    return jsonify({"error": "Invalid request"}), 400


# Home route to render the "Check My Ability" template
@app.route('/')
def home():
    return render_template('check.html')  # Ensure this matches your template file


# Quiz route to render quiz questions
@app.route('/quiz')
def quiz():
    selected_topics = request.args.to_dict()
    return render_template('quiz.html', topics=selected_topics)


@app.route('/check')
def check_ability():
    return render_template('check.html')

app.register_blueprint(syllabus_bp)

if __name__ == '__main__':
    app.run(debug=True)


