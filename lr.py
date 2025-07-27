import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import datetime

# Load the entire workbook and get sheet names
file_path = 'C:/Users/Nithish Kumar B/Desktop/mini project/student_management/Data/students_data/nisarga.xlsx'
sheets = pd.ExcelFile(file_path).sheet_names

# Function to convert "time_spent" to seconds
def time_to_seconds(time_val):
    if isinstance(time_val, datetime.time):
        return time_val.hour * 3600 + time_val.minute * 60 + time_val.second
    elif isinstance(time_val, str):
        minutes, seconds = map(int, time_val.split(":"))
        return minutes * 60 + seconds
    return 0

# Loop through each sheet and perform analysis
for sheet_name in sheets:
    # Load data from the current sheet
    data = pd.read_excel(file_path, sheet_name=sheet_name)
    
    # Preprocess data
    data['Time_Spent_Seconds'] = data['time_spent'].apply(time_to_seconds)
    data['Correct'] = (data['answer'] == data['correct_answer']).astype(int)
    data['Answer_Encoded'] = data['answer'].astype('category').cat.codes
    
    # Select features and target variable
    X = data[['Time_Spent_Seconds', 'level', 'Answer_Encoded']]
    y = data['Correct']
    
    # Train-test split and model training
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LogisticRegression()
    model.fit(X_train, y_train)
    
    # Level-based performance analysis
    level_performance = data.groupby('level')['Correct'].mean() * 100
    weakest_level = level_performance.idxmin()
    strongest_level = level_performance.idxmax()
    overall_performance = data['Correct'].mean() * 100
    
    # Display results for the current sheet
    print(f"\n=== Performance Report for {sheet_name} ===")
    print("Level-based performance (% accuracy):")
    print(level_performance.round(2))
    print(f"Weakest Level: Level {weakest_level} with {level_performance[weakest_level]:.2f}% accuracy")
    print(f"Strongest Level: Level {strongest_level} with {level_performance[strongest_level]:.2f}% accuracy")
    print(f"Overall Performance: {overall_performance:.2f}% accuracy\n")
