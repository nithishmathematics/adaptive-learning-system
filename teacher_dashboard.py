from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from pathlib import Path
import pandas as pd

teacher_routes = Blueprint('teacher_routes', __name__, template_folder='templates')

DATA_FOLDER = Path('data/students_data') # Data folder for student files

def search_student(name):
    student_file = DATA_FOLDER / f"{name}.xlsx"
    if student_file.exists():
        try:
            student_data = pd.read_excel(student_file)
            if 'Name' in student_data.columns and name in student_data['Name'].values:
                student_info = student_data[student_data['Name'] == name].iloc[0].to_dict()
                performance = student_info.get('Performance', 'N/A')
                return {'exists': True, 'name': name, 'performance': performance}
            else:
                return {'exists': False, 'message': 'Name column missing or student not found'}
        except Exception as e:
            return {'exists': False, 'message': f"Error reading file: {e}"}
    return {'exists': False, 'message': 'File not found'}


@teacher_routes.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    
    if request.method == 'POST':
        search_name = request.form.get('search_name')

        # Search for the student
        result = search_student(search_name)
        if result['exists']:
            return jsonify({'status': 'success', 'name': result['name'], 'performance': result['performance']})
        else:
            return jsonify({'status': 'not_found', 'message': f"Student {search_name} not found."})

    # Render the teacher dashboard page
    return render_template('teacher_dashboard.html', teacher_name="Teacher Name")

@teacher_routes.route('/change_password', methods=['GET', 'POST'])
def change_password():
    """
    Change Password route for the teacher.
    """
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        # Perform password update logic here (e.g., verify current password, update in the database)
        flash('Password changed successfully.', 'success')
        return redirect(url_for('teacher_routes.dashboard'))
    return render_template('change_password.html')

@teacher_routes.route('/logout')
def logout():
   
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@teacher_routes.route('/history')
def history():
    """
    Displays the Teacher's history.
    """
    # Add logic to fetch history data (e.g., logs or actions performed by the teacher)
    history_data = [
        {'date': '2024-11-10', 'action': 'Searched for student Nithesh'},
        {'date': '2024-11-11', 'action': 'Viewed student performance for Chapter 3'},
    ]
    return render_template('history.html', history=history_data)

@teacher_routes.route('/search_student', methods=['GET'])
def search_student():
    name = request.args.get('name')
    student_file = DATA_FOLDER / f"{name}.xlsx"
    if student_file.exists():
        student_data = pd.read_excel(student_file)
        return jsonify({'exists': True, 'name': name})
    return jsonify({'exists': False, 'message': 'Student not found'})

    
@teacher_routes.route('/status/<string:name>', methods=['GET'])
def status(name):
    student_file = DATA_FOLDER / f"{name}.xlsx"
    
    if not student_file.exists():
        return render_template('error.html', message=f"Student file for {name} not found.")
    
    # Load the data from the 'Cal' sheet
    student_data = pd.read_excel(student_file, sheet_name='cal')
    
    # Convert data to dictionary for rendering in the template
    table_data = student_data.to_dict(orient='records')
    columns = student_data.columns.tolist()
    
    return render_template(
        'status.html', 
        student_name=name, 
        table_data=table_data, 
        columns=columns
    )
