import numpy as np
import sympy as sp
import pandas as pd
import datetime

# Function to calculate the performance based on time spent, difficulty, and correctness
def performance_function(time_spent, difficulty, correctness_score):
    a = 1  # Coefficient for time spent
    b = 0.5  # Coefficient for difficulty
    c = 2  # Coefficient for correctness
    return a * time_spent - b * (difficulty ** 2) + c * correctness_score

# Function to calculate derivatives
def calculate_derivatives(time_spent, difficulty, correctness_score):
    t, d = sp.symbols('t d')
    performance = performance_function(t, d, sp.symbols('correctness_score'))
    
    derivative_time = sp.diff(performance, t)
    derivative_difficulty = sp.diff(performance, d)
    
    derivative_time_value = derivative_time.subs({t: time_spent, d: difficulty})
    derivative_difficulty_value = derivative_difficulty.subs({t: time_spent, d: difficulty})
    
    return derivative_time_value, derivative_difficulty_value

# Function to calculate gradient descent
def gradient_descent(current_difficulty, learning_rate):
    _, gradient = calculate_derivatives(1, current_difficulty, 0)  # Assuming time_spent = 1 for simplicity
    new_difficulty = current_difficulty - learning_rate * gradient
    return new_difficulty

# Function to calculate total performance over time
def total_performance(integral_time, difficulty, correctness_score):
    t = sp.symbols('t')
    performance = performance_function(t, difficulty, correctness_score)
    total_perf = sp.integrate(performance, (t, 0, integral_time))
    
    return total_perf

# Function to convert "time_spent" to seconds
def time_to_seconds(time_val):
    if isinstance(time_val, datetime.time):
        return time_val.hour * 3600 + time_val.minute * 60 + time_val.second
    elif isinstance(time_val, str):
        minutes, seconds = map(int, time_val.split(":"))
        return minutes * 60 + seconds
    return 0

# Expected times in minutes for each level
expected_times = {
    1: (1, 1),          # Level 1: Expected time is exactly 1 minute.
    2: (1.5, 2),        # Level 2: Expected time is between 1.5 and 2 minutes.
    3: (2.5, 3.5),      # Level 3: Expected time is between 2.5 and 3.5 minutes.
    4: (4.5, 5)         # Level 4: Expected time is between 4.5 and 5 minutes.
}

# Function to adjust difficulty level based on performance and expected times
def adjust_difficulty(current_level, actual_time_spent):
    expected_min_time, expected_max_time = expected_times[current_level]
    
    if actual_time_spent < expected_min_time:
        return max(current_level - 1, 1)   # Decrease level if too fast
    elif actual_time_spent > expected_max_time:
        return min(current_level + 1, 4)   # Increase level if too slow
    
    return current_level

# Function to categorize performance into qualitative assessments
def categorize_performance(total_performance):
    if total_performance > 10:
        return "Good", "(Excellent)"
    elif total_performance > 5:
        return "Average", "(Satisfactory)"
    elif total_performance > 0:
        return "Poor", "(Needs Improvement)"
    else:
        return "Bad", "(Unsatisfactory)"

# Function to process Excel sheets and summarize results
def process_excel(file_path):
    excel_data = pd.ExcelFile(file_path)
    
    overall_results = {}
    
    for sheet_name in excel_data.sheet_names:
        df = excel_data.parse(sheet_name)

        df['time_spent'] = df['time_spent'].apply(time_to_seconds) / 60   # Convert seconds to minutes
        
        total_performance_sum = 0
        total_time_spent = 0
        total_levels = []
        
        for index, row in df.iterrows():
            level = row['level']
            actual_time_spent = row['time_spent']
            learning_rate = 0.1
            
            # Calculate correctness score based on answers
            correctness_score = int(row['answer'] == row['correct_answer']) 
            
            derivative_time, derivative_difficulty = calculate_derivatives(actual_time_spent, level, correctness_score)

            new_difficulty = gradient_descent(level, learning_rate)

            integral_time = actual_time_spent / len(df) if len(df) > 0 else actual_time_spent  
            performance_value = total_performance(integral_time, level, correctness_score)

            # Adjust difficulty based on actual time spent compared to expected times
            adjusted_level = adjust_difficulty(level, actual_time_spent)

            total_performance_sum += performance_value.evalf()
            total_time_spent += actual_time_spent
            total_levels.append(adjusted_level)

            print(f"Sheet: {sheet_name}, Row: {index + 1}")
            print(f"Rate of change of performance with respect to time: {derivative_time}")
            print(f"Rate of change of performance with respect to difficulty: {derivative_difficulty}")
            print(f"Updated difficulty level after gradient descent: {new_difficulty}")
            print(f"Adjusted Difficulty Level based on actual time spent: {adjusted_level}")

        average_level = sum(total_levels) / len(total_levels) if total_levels else 0
        
        # Categorize the overall performance into qualitative assessments
        category_description, category_note = categorize_performance(total_performance_sum)

        overall_results[sheet_name] = {
            "Total Performance": total_performance_sum,
            "Performance Category": f"{category_description} {category_note}",
            "Total Time Spent (minutes)": total_time_spent,
            "Average Difficulty Level": average_level,
        }
    
    return overall_results

# User input for file path
file_path = 'C:/Users/Nithish Kumar B/Desktop/mini project/student_management/Data/students_data/nisarga.xlsx'

# Process the Excel file and generate reports
results = process_excel(file_path)

# Print overall results summary for each sheet
print("\nSummary of Results:")
for sheet_name, metrics in results.items():
    print(f"\nSheet: {sheet_name}")
    print(f"Total Performance over specified hours: {metrics['Total Performance']:.2f} ({metrics['Performance Category']})")
    print(f"Total Time Spent (minutes): {metrics['Total Time Spent (minutes)']:.2f}")
    print(f"Average Difficulty Level: {metrics['Average Difficulty Level']:.2f}")