print("""
import numpy as np
import pandas as pd
from sklearn.datasets import load_diabetes, load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.utils import to_categorical

# Load datasets
def load_datasets():
    # Diabetes dataset
    diabetes = load_diabetes()
    X_diabetes, y_diabetes = diabetes.data, diabetes.target

    # Cancer dataset
    cancer = load_breast_cancer()
    X_cancer, y_cancer = cancer.data, cancer.target

    # Sonar dataset
    sonar_data = pd.read_csv('https://archive.ics.uci.edu/ml/machine-learning-databases/undocumented/connectionist-bench/sonar/sonar.all-data', header=None)
    X_sonar = sonar_data.iloc[:, :-1].values
    y_sonar = LabelEncoder().fit_transform(sonar_data.iloc[:, -1])

    return (X_diabetes, y_diabetes), (X_cancer, y_cancer), (X_sonar, y_sonar)

# Preprocess datasets
def preprocess_data(X, y, classification=False):
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    if classification:
        y = to_categorical(y)
    return X, y

# Build a neural network
def build_model(input_dim, output_dim, activation='relu', classification=False):
    model = Sequential()
    model.add(Input(shape=(input_dim,)))  # Define the input shape here
    model.add(Dense(64, activation=activation))
    model.add(Dense(32, activation=activation))
    if classification:
        model.add(Dense(output_dim, activation='softmax'))
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    else:
        model.add(Dense(1, activation='linear'))
        model.compile(optimizer='adam', loss='mse', metrics=['mse'])
    return model

# Train and evaluate the model
def train_and_evaluate(X_train, X_test, y_train, y_test, model):
    model.fit(X_train, y_train, epochs=20, batch_size=32, verbose=0)
    metrics = model.evaluate(X_test, y_test, verbose=0)
    return metrics

# Main
(X_diabetes, y_diabetes), (X_cancer, y_cancer), (X_sonar, y_sonar) = load_datasets()

# Process datasets
X_diabetes, y_diabetes = preprocess_data(X_diabetes, y_diabetes)
X_cancer, y_cancer = preprocess_data(X_cancer, y_cancer, classification=True)
X_sonar, y_sonar = preprocess_data(X_sonar, y_sonar, classification=True)

# Split datasets
X_d_train, X_d_test, y_d_train, y_d_test = train_test_split(X_diabetes, y_diabetes, test_size=0.2, random_state=42)
X_c_train, X_c_test, y_c_train, y_c_test = train_test_split(X_cancer, y_cancer, test_size=0.2, random_state=42)
X_s_train, X_s_test, y_s_train, y_s_test = train_test_split(X_sonar, y_sonar, test_size=0.2, random_state=42)

# Train and evaluate models for each dataset
activations = ['relu', 'sigmoid', 'tanh']

for activation in activations:
    print(f"\nActivation Function: {activation}\n")

    # Diabetes (Regression)
    model_diabetes = build_model(X_diabetes.shape[1], 1, activation=activation, classification=False)
    mse_diabetes, _ = train_and_evaluate(X_d_train, X_d_test, y_d_train, y_d_test, model_diabetes)
    print(f"Diabetes Dataset MSE: {mse_diabetes:.4f}")

    # Cancer (Classification)
    model_cancer = build_model(X_cancer.shape[1], y_cancer.shape[1], activation=activation, classification=True)
    loss_cancer, acc_cancer = train_and_evaluate(X_c_train, X_c_test, y_c_train, y_c_test, model_cancer)
    print(f"Cancer Dataset Accuracy: {acc_cancer:.4f}")

    # Sonar (Classification)
    model_sonar = build_model(X_sonar.shape[1], y_sonar.shape[1], activation=activation, classification=True)
    loss_sonar, acc_sonar = train_and_evaluate(X_s_train, X_s_test, y_s_train, y_s_test, model_sonar)
    print(f"Sonar Dataset Accuracy: {acc_sonar:.4f}")

""")