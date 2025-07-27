from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from pathlib import Path
import pandas as pd

hod_routes = Blueprint('hod_routes', __name__, template_folder='templates')

DATA_FOLDER = Path('data')  # Data folder for student and teacher files

def search_user(user_type, name):
    """
    Searches for a user in the data folder based on user_type (student/teacher) and name.
    """
    user_file = DATA_FOLDER / f"{user_type.lower()}s.xlsx"
    if user_file.exists():
        user_data = pd.read_excel(user_file)
        if name in user_data['Name'].values:
            return True
    return False

@hod_routes.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    """
    HoD Dashboard route.
    """
    if request.method == 'POST':
        search_type = request.form.get('search_type')  # 'student' or 'teacher'
        search_name = request.form.get('search_name')

        # Search for the user
        if search_user(search_type, search_name):
            return jsonify({'status': 'success', 'name': search_name, 'type': search_type})
        else:
            return jsonify({'status': 'not_found', 'message': f"{search_type.capitalize()} {search_name} not found."})

    # Render the dashboard page
    return render_template('hod_dashboard.html', hod_name="HoD Name")

@hod_routes.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        # Perform password update logic here
        flash('Password changed successfully.', 'success')
        return redirect(url_for('hod_routes.dashboard'))
    return render_template('change_password.html')



@hod_routes.route('/logout')
def logout():
    """
    Logout functionality.
    """
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@hod_routes.route('/history')
def history():
    """
    Displays the HoD history.
    """
    # Add logic to fetch history data (e.g., logs or analytics)
    history_data = [
        {'date': '2024-11-01', 'action': 'Viewed teacher data'},
        {'date': '2024-11-02', 'action': 'Searched for student Nithesh'},
    ]
    return render_template('history.html', history=history_data)

@hod_routes.route('/status/<string:name>', methods=['GET'])
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

@hod_routes.route('/search_student', methods=['GET'])
def search_student():
    name = request.args.get('name')
    student_file = DATA_FOLDER / f"{name}.xlsx"
    if student_file.exists():
        student_data = pd.read_excel(student_file)
        return jsonify({'exists': True, 'name': name})
    return jsonify({'exists': False, 'message': 'Student not found'})