import os
import pandas as pd
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from pathlib import Path
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

student_routes = Blueprint('student_routes', __name__, template_folder='templates')

SYLLABUS_FOLDER = Path('syllabus')
DATA_FOLDER = Path('data/students_data')


def get_chapters(subject):
    subject_folder = SYLLABUS_FOLDER / subject.lower()
    if subject_folder.exists():
        return [chapter.name for chapter in subject_folder.iterdir() if chapter.is_dir()]
    return []


def get_topics(subject, chapter):
    chapter_folder = SYLLABUS_FOLDER / subject.lower() / chapter
    if chapter_folder.exists():
        return [topic.name for topic in chapter_folder.iterdir() if topic.is_dir()]
    return []


@student_routes.route('/dashboard')
def dashboard():
    subjects = ["Physics", "Chemistry", "Mathematics", "Biology"]
    subject_chapters = {subject: get_chapters(subject) for subject in subjects}
    return render_template('student_dashboard.html', subjects=subjects,
                           subject_chapters=subject_chapters)

@student_routes.route('/get_topics', methods=['POST'])
def get_topics_route():
    subject = request.form.get('subject')
    chapter = request.form.get('chapter')
    topics = get_topics(subject, chapter)
    return jsonify(topics=topics)

@student_routes.route('/quiz/<subject>/<chapter>/<topic>', methods=['GET'])
def quiz_page(subject, chapter, topic):
    topic_folder = SYLLABUS_FOLDER / subject.lower() / chapter / topic
    questions_file = topic_folder / 'questions.xlsx'

    if questions_file.exists():
        df = pd.read_excel(questions_file)

        # Ensure we don't sample more questions than available
        num_questions_to_sample = min(10, len(df))
        selected_questions = df.sample(n=num_questions_to_sample).reset_index(drop=True)

        questions_list = selected_questions.to_dict(orient='records')
        correct_answers = selected_questions['Correct'].tolist()

        return render_template('quiz.html', subject=subject, chapter=chapter,
                               topic=topic, questions=questions_list, correct_answers=correct_answers)

    return "Questions not found", 404


@student_routes.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    if not session.get("username"):
        return jsonify(message="Session expired. Please log in again."), 401

    data = request.json
    if not data:
        return jsonify(message="Invalid data format"), 400

    subject = data.get('subject')
    test_name = data.get('test_name')
    user_answers = data.get('user_answers')
    correct_answers = data.get('correct_answers')
    levels = data.get('levels')
    time_spent_list = data.get('time_spent_list')
    total_questions = data.get('total_questions', 0)

    if not subject or not test_name or not user_answers or not correct_answers:
        return jsonify(message="Missing required fields."), 400

    student_name = session.get("username")

    # Prepare quiz data in the required format
    quiz_data = [
        {
            'Question_No': i + 1,
            'Level': levels[i] if levels else "N/A",
            'Time_Spent': time_spent_list[i] if time_spent_list else "N/A",
            'Answer': user_answers[i] if user_answers else "N/A",
            'Test_Name': test_name,
        }
        for i in range(total_questions)
    ]

    try:
        # Save to the Excel file
        student_file = DATA_FOLDER / f"{student_name}.xlsx"
        with pd.ExcelWriter(student_file, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
            pd.DataFrame(quiz_data).to_excel(
                writer, sheet_name=subject, index=False, header=not writer.sheets.get(subject)
            )

        return jsonify(message="Quiz results saved successfully!"), 200
    except Exception as e:
        return jsonify(message=f"Error saving quiz results: {e}"), 500


@student_routes.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        # Perform password update logic here (add actual logic)
        flash('Password changed successfully.', 'success')
        return redirect(url_for('student_routes.dashboard'))
    
    return render_template('change_password.html')

@student_routes.route('/learning_status')
def learning_status():
    # Path to the Excel file
    excel_file = os.path.join(DATA_FOLDER, 'nisarga.xlsx')

    # Check if the file exists
    if not os.path.exists(excel_file):
        flash("Excel file not found!", "error")
        return redirect(url_for('student_routes.dashboard'))

    # Read the data from the Excel file
    try:
        cal_data = pd.read_excel(excel_file, sheet_name='cal')
    except Exception as e:
        flash(f"Error reading Excel file: {e}", "error")
        return redirect(url_for('student_routes.dashboard'))

    # Generate graphs
    graph_folder = os.path.join('static', 'graphs')
    os.makedirs(graph_folder, exist_ok=True)

    # Extract data for graphs
    subjects = cal_data['Sheet Name']
    lr_performance = cal_data['Total Performance LR']
    rnn_performance = cal_data['Total Performance RNN']
    difficulty_level = cal_data['Average Difficulty Level']
    time_spent = cal_data['Total Time Spent (minutes)']

    graphs = {}

    # Generate LR Model Performance graph
    plt.figure(figsize=(10, 6))
    plt.bar(subjects, lr_performance, color='blue', alpha=0.7)
    plt.title('Overall Performance rate of the subjects')
    plt.xlabel('Subjects')
    plt.ylabel('Performance')
    plt.xticks(rotation=45)
    plt.tight_layout()
    lr_graph_path = os.path.join(graph_folder, 'lr_model_performance.png')
    plt.savefig(lr_graph_path)
    plt.close()
    graphs['lr'] = lr_graph_path

    # Generate RNN Model Performance graph
    plt.figure(figsize=(10, 6))
    plt.bar(subjects, rnn_performance, color='green', alpha=0.7)
    plt.title('Prediction of correct answers of Next 10 questions')
    plt.xlabel('Subjects')
    plt.ylabel('Performance')
    plt.xticks(rotation=45)
    plt.tight_layout()
    rnn_graph_path = os.path.join(graph_folder, 'rnn_model_performance.png')
    plt.savefig(rnn_graph_path)
    plt.close()
    graphs['rnn'] = rnn_graph_path

    # Generate Average Difficulty Level graph
    plt.figure(figsize=(10, 6))
    plt.bar(subjects, difficulty_level, color='orange', alpha=0.7)
    plt.title('Average Difficulty Level for All Subjects')
    plt.xlabel('Subjects')
    plt.ylabel('Difficulty Level')
    plt.xticks(rotation=45)
    plt.tight_layout()
    difficulty_graph_path = os.path.join(graph_folder, 'average_difficulty_level.png')
    plt.savefig(difficulty_graph_path)
    plt.close()
    graphs['difficulty'] = difficulty_graph_path

    # Generate Total Time Spent graph
    plt.figure(figsize=(10, 6))
    plt.bar(subjects, time_spent, color='red', alpha=0.7)
    plt.title('Total Time Spent for All Subjects')
    plt.xlabel('Subjects')
    plt.ylabel('Time Spent (minutes)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    time_graph_path = os.path.join(graph_folder, 'total_time_spent.png')
    plt.savefig(time_graph_path)
    plt.close()
    graphs['time'] = time_graph_path

    # Return the learning status page
    graph_urls = {key: url_for('static', filename=f'graphs/{os.path.basename(value)}') for key, value in graphs.items()}
    return render_template('learning_status.html', graphs=graph_urls)

@student_routes.route('/api/chapters/<subject>', methods=['GET'])
def api_get_chapters(subject):
    chapters = get_chapters(subject)
    return jsonify(chapters=chapters)

@student_routes.route('/api/topics/<subject>/<chapter>', methods=['GET'])
def api_get_topics(subject, chapter):
    topics = get_topics(subject, chapter)
    return jsonify(topics=topics)

@student_routes.route('/check')
def check_ability():
    return render_template('check.html')

@student_routes.route('/entrance_exam')
def entrance_exam():
    return render_template('entrance_exam.html')

import logging
logging.basicConfig(level=logging.DEBUG)

def get_chapters(subject):
    subject_folder = SYLLABUS_FOLDER / subject.lower()
    logging.debug(f"Looking for chapters in: {subject_folder}")
    if subject_folder.exists():
        chapters = [chapter.name for chapter in subject_folder.iterdir() if chapter.is_dir()]
        logging.debug(f"Found chapters for {subject}: {chapters}")
        return chapters
    logging.error(f"Subject folder not found: {subject_folder}")
    return []



