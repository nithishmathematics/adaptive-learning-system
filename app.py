from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
import os
import shutil
from student_dashboard import student_routes  # Import the student blueprint
from hod_dashboard import hod_routes
from teacher_dashboard import teacher_routes
app = Flask(__name__)
app.secret_key = "your_secret_key"

# Register the student blueprint
app.register_blueprint(student_routes, url_prefix='/student')
app.register_blueprint(hod_routes, url_prefix='/hod')
app.register_blueprint(teacher_routes, url_prefix='/teacher')
# File paths for user data and specific roles
BASE_DATA_DIR = "Data"
SIGNUP_RECORD = os.path.join(BASE_DATA_DIR, "users_data.xlsx")
STUDENT_DATA_DIR = os.path.join(BASE_DATA_DIR, "students_data")
TEACHER_DATA_DIR = os.path.join(BASE_DATA_DIR, "teachers_data")
HOD_DATA_DIR = os.path.join(BASE_DATA_DIR, "hods_data")

# Create necessary directories if they don't exist
for dir_path in [BASE_DATA_DIR, STUDENT_DATA_DIR, TEACHER_DATA_DIR, HOD_DATA_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

# Load user data from Excel for login validation
def load_user_data():
    try:
        return pd.read_excel(SIGNUP_RECORD)
    except FileNotFoundError:
        return pd.DataFrame(columns=["username", "password", "role"])

# Save user data back to Excel for registration
def save_user_data(df):
    df.to_excel(SIGNUP_RECORD, index=False)

# Create a new file for a user
def create_role_file(username, role):
    templates = {
        'student': os.path.join(STUDENT_DATA_DIR, "nithish.xlsx"),
        'hod': os.path.join(HOD_DATA_DIR, "gowri.xlsx"),
        'teacher': os.path.join(TEACHER_DATA_DIR, "anushree.xlsx")
    }

    if role not in templates:
        return None

    template_file = templates[role]

    if role == 'student':
        role_folder = STUDENT_DATA_DIR
    elif role == 'hod':
        role_folder = HOD_DATA_DIR
    elif role == 'teacher':
        role_folder = TEACHER_DATA_DIR
    
    user_file_path = os.path.join(role_folder, f"{username}.xlsx")
    
    if os.path.exists(template_file):
        shutil.copy(template_file, user_file_path)
        df = pd.read_excel(user_file_path)
        if 'Detail' in df.columns and 'Value' in df.columns:
            df.loc[df['Detail'] == 'Name', 'Value'] = username
            df.loc[df['Detail'] == 'Role', 'Value'] = role
            df.to_excel(user_file_path, index=False)
        else:
            return f"Template file does not have the required columns."

    return user_file_path

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        password = request.form['password'].strip()
        role = request.form['role'].strip().lower()

        if not username or not password or not role:
            return "All fields are required."

        users = load_user_data()
        user = users[users['username'].str.lower() == username]

        if not user.empty:
            user_password = str(user.iloc[0]['password']).strip()
            user_role = str(user.iloc[0]['role']).strip().lower()

            if user_password == password:
                if user_role == role:
                    session['username'] = username
                    session['role'] = role

                    if role == 'student':
                        return redirect(url_for('student_routes.dashboard'))
                    elif role == 'hod':
                        return redirect(url_for('hod_routes.dashboard'))
                    elif role == 'teacher':
                        return redirect(url_for('teacher_routes.dashboard'))
                else:
                    return "Invalid role."
            else:
                return "Invalid password."
        else:
            return "Username not found."

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        password = request.form['password'].strip()
        role = request.form['role'].strip().lower()

        users = load_user_data()

        if not users[users['username'].str.lower() == username].empty:
            return "Username already exists."

        new_user = {
            'username': username,
            'password': password,
            'role': role
        }

        users = pd.concat([users, pd.DataFrame([new_user])], ignore_index=True)
        save_user_data(users)
        create_role_file(username, role)

        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)