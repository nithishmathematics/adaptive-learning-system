import pandas as pd
import numpy as np
import datetime
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from sklearn.utils import class_weight
import tensorflow as tf
import os

# Set a global random seed for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

# File path for the Excel workbook
file_path = 'C:/Users/Nithish Kumar B/Desktop/mini project/project/Data/students_data/nisarga.xlsx'

# Function to convert "time_spent" to seconds
def time_to_seconds(time_val):
    try:
        if isinstance(time_val, datetime.time):
            return time_val.hour * 3600 + time_val.minute * 60 + time_val.second
        elif isinstance(time_val, str):
            minutes, seconds = map(int, time_val.split(":"))
            return minutes * 60 + seconds
    except (ValueError, AttributeError):
        return 0  # Handle invalid formats gracefully
    return 0

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

# Logistic Regression Analysis Function
def logistic_regression_analysis(data):
    try:
        data['Time_Spent_Seconds'] = data['time_spent'].apply(time_to_seconds)
        data['Correct'] = (data['answer'] == data['correct_answer']).astype(int)

        # Select features and target variable
        X = data[['Time_Spent_Seconds', 'level']]
        y = data['Correct']

        # Check if there are at least 2 unique classes in y
        if len(y.unique()) < 2:
            print(f"Skipping analysis due to insufficient classes.")
            return pd.Series(dtype=float), None, None

        # Train-test split and model training
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LogisticRegression()
        model.fit(X_train, y_train)

        # Level-based performance analysis
        level_performance = data.groupby('level')['Correct'].mean() * 100
        overall_performance = data['Correct'].mean() * 100
        weakest_level = level_performance.idxmin()
        strongest_level = level_performance.idxmax()

        print(f"Weakest Level: Level {weakest_level} with {level_performance[weakest_level]:.2f}% accuracy")
        print(f"Strongest Level: Level {strongest_level} with {level_performance[strongest_level]:.2f}% accuracy")
        
        return level_performance, overall_performance, (weakest_level, strongest_level)
    except Exception as e:
        print(f"Error during logistic regression analysis: {e}")
        return pd.Series(dtype=float), None, None

# Recurrent Neural Network Analysis Function
def recurrent_neural_network_analysis(data):
    try:
        data['Time_Spent_Seconds'] = data['time_spent'].apply(time_to_seconds)
        data['Correct'] = (data['answer'] == data['correct_answer']).astype(int)

        # Prepare input for RNN
        X = data[['Time_Spent_Seconds', 'level']].values
        y = data['Correct'].values

        # Reshape for RNN input
        sequence_length = 5
        X_sequences, y_sequences = [], []

        for i in range(len(X) - sequence_length):
            X_sequences.append(X[i:i + sequence_length])
            y_sequences.append(y[i + sequence_length])
        
        if not X_sequences:  # Handle edge case with insufficient data
            print("Insufficient data for RNN analysis.")
            return {}

        X_sequences, y_sequences = np.array(X_sequences), np.array(y_sequences)

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X_sequences, y_sequences, test_size=0.2, random_state=42)

        # Define and compile LSTM model
        model = Sequential()
        model.add(LSTM(units=50, activation='relu', input_shape=(X_train.shape[1], X_train.shape[2])))
        model.add(Dense(1, activation='sigmoid'))
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

        # Calculate sample weights based on class distribution
        class_weights = class_weight.compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
        sample_weights = np.array([class_weights[int(label)] for label in y_train])

        # Train the model with sample weights
        model.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_test, y_test), sample_weight=sample_weights)

        # Performance predictions for each level in the current subject
        levels = data['level'].unique()
        level_predictions = {}

        for level in levels:
            predicted_correct_answers = 0
            latest_sequence = X_sequences[-1]

            for _ in range(10):  # Predict next 10 questions at this level
                next_question = np.expand_dims(latest_sequence, axis=0)
                predicted_probability = model.predict(next_question)[0][0]

                if predicted_probability > 0.5:
                    predicted_correct_answers += 1

                new_time_spent = np.mean(latest_sequence[:, 0])
                new_question = [new_time_spent, level]
                latest_sequence = np.vstack([latest_sequence[1:], new_question])

            level_predictions[level] = predicted_correct_answers

        return level_predictions
    except Exception as e:
        print(f"Error during RNN analysis: {e}")
        return {}

# Function to process Excel file and update sheets
def process_excel(file_path):
    try:
        excel_data = pd.ExcelFile(file_path)

        cal_results = []
        progress_results = []

        expected_performance_values_lr = {1: 15.00, 2: 20.00, 3: 25.00, 4: 30.00}
        expected_performance_values_rnn = {1: 5.00, 2: 10.00, 3: 15.00, 4: 20.00}

        for sheet_name in excel_data.sheet_names:
            if sheet_name in ["progress", "cal"]:
                continue
            
            df = excel_data.parse(sheet_name)
            lr_performance, overall_lr_performance, lr_levels_info = logistic_regression_analysis(df)
            rnn_predictions = recurrent_neural_network_analysis(df)

            if lr_levels_info is None:
                print(f"Skipping sheet {sheet_name} due to insufficient data.")
                continue

            total_time_spent_minutes = df['time_spent'].apply(time_to_seconds).sum() / 60

            total_lr_performance_sum = lr_performance.sum() + (len(lr_performance) * expected_performance_values_lr.get(lr_levels_info[0], 0))
            total_rnn_performance_sum = sum([expected_performance_values_rnn.get(level, 0) for level in rnn_predictions.keys()])

            category_description_lr, category_note_lr = categorize_performance(total_lr_performance_sum)
            category_description_rnn, category_note_rnn = categorize_performance(total_rnn_performance_sum)

            cal_results.append({
                "Sheet Name": sheet_name,
                "Total Performance LR": total_lr_performance_sum,
                "Total Performance RNN": total_rnn_performance_sum,
                "Total Time Spent (minutes)": total_time_spent_minutes,
                "Average Difficulty Level": df['level'].mean(),
                "Performance Category LR": f"{category_description_lr} {category_note_lr}",
                "Performance Category RNN": f"{category_description_rnn} {category_note_rnn}",
            })

            progress_results.append({
                "model_name": "lr",
                "level": lr_levels_info[0],
                "performance": overall_lr_performance + expected_performance_values_lr.get(lr_levels_info[0], 0),
                "Sheet Name": sheet_name,
            })

            for level, performance in rnn_predictions.items():
                progress_results.append({
                    "model_name": "recurrent",
                    "level": level,
                    "performance": performance + expected_performance_values_rnn.get(level, 0),
                    "Sheet Name": sheet_name,
                })

        # Save results back to Excel
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            pd.DataFrame(cal_results).to_excel(writer, sheet_name='cal', index=False)
            pd.DataFrame(progress_results).to_excel(writer, sheet_name='progress', index=False)
    except Exception as e:
        print(f"Error processing Excel file: {e}")

# Run the processing function
process_excel(file_path)
