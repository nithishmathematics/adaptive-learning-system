import pandas as pd
import numpy as np
import datetime
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from sklearn.utils import class_weight
import tensorflow as tf

# Set a global random seed
np.random.seed(42)
tf.random.set_seed(42)

# Load the workbook and get sheet names
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

all_data = pd.concat([pd.read_excel(file_path, sheet_name=sheet) for sheet in sheets])
all_data['Time_Spent_Seconds'] = all_data['time_spent'].apply(time_to_seconds)
all_data['Answer_Encoded'] = all_data['answer'].astype('category').cat.codes

# Fit scaler on the combined data to ensure consistent scaling across sheets
scaler = MinMaxScaler()
scaler.fit(all_data[['Time_Spent_Seconds', 'level', 'Answer_Encoded']])

# Store predictions for all subjects
all_level_predictions = {}

# Process each sheet for predictions
for sheet_name in sheets:
    # Load and preprocess data
    data = pd.read_excel(file_path, sheet_name=sheet_name)
    data['Time_Spent_Seconds'] = data['time_spent'].apply(time_to_seconds)
    data['Correct'] = (data['answer'] == data['correct_answer']).astype(int)
    data['Answer_Encoded'] = data['answer'].astype('category').cat.codes
    
    # Apply consistent scaling
    X = data[['Time_Spent_Seconds', 'level', 'Answer_Encoded']].values
    y = data['Correct'].values
    
    # Reshape data for RNN
    sequence_length = 5
    X_sequences, y_sequences = [], []
    for i in range(len(X) - sequence_length):
        X_sequences.append(X[i:i+sequence_length])
        y_sequences.append(y[i+sequence_length])
    X_sequences, y_sequences = np.array(X_sequences), np.array(y_sequences)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X_sequences, y_sequences, test_size=0.2, random_state=42)
    
    # Define and compile the LSTM model
    model = Sequential()
    model.add(LSTM(units=50, activation='relu', input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    
    # Calculate sample weights based on class distribution
    class_weights = class_weight.compute_class_weight(
        class_weight='balanced',
        classes=np.unique(y_train),
        y=y_train
    )

    # Check if class_weights has more than one class
    if len(class_weights) > 1:
        sample_weights = np.array([class_weights[int(label)] for label in y_train])
    else:
        sample_weights = np.ones_like(y_train)  # All weights are set to 1 if there's only one class

    # Train the model with sample weights
    model.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_test, y_test), sample_weight=sample_weights)

    # Performance predictions for each level in the current subject
    levels = data['level'].unique()
    level_predictions = {}

    for level in levels:
        predicted_correct_answers = 0
        latest_sequence = X_sequences[-1]
        
        # Predict next 10 questions at this level
        for _ in range(10):
            next_question = np.expand_dims(latest_sequence, axis=0)
            predicted_probability = model.predict(next_question)[0][0]
            
            # Adjust the threshold based on past performance
            if predicted_probability > 0.5:
                predicted_correct_answers += 1
            
            new_answer_encoded = 1 if predicted_probability > 0.5 else 0
            new_time_spent = np.mean(latest_sequence[:, 0])  # Average time spent in the last sequence
            new_question = [new_time_spent, level, new_answer_encoded]
            latest_sequence = np.vstack([latest_sequence[1:], new_question])
        
        # Store predictions for the current level
        level_predictions[level] = predicted_correct_answers

    # Store predictions for the current subject
    all_level_predictions[sheet_name] = level_predictions

# Display results for all subjects
for subject, predictions in all_level_predictions.items():
    print(f"\n=== Performance Prediction Report for {subject} ===")
    for level, correct_answers in predictions.items():
        print(f"Level {level}: Predicted Correct Answers out of 10 = {correct_answers}")