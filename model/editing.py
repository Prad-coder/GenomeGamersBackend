import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

# Load the dataset
data = pd.read_csv('gene_editing.csv')

# Preprocess the data
# Drop unnecessary columns
data = data.drop(columns=['SequenceID', 'ScreenID', 'Replicate', 'Library', 'ModelConditionID'], errors='ignore')

# Handle missing values
data = data.dropna(subset=['PassesQC', 'ExcludeFromCRISPRCombined'])

# Convert categorical columns to numeric
categorical_columns = ['ScreenType', 'DrugTreated', 'Library']
label_encoders = {}
for col in categorical_columns:
    if col in data.columns:
        le = LabelEncoder()
        data[col] = le.fit_transform(data[col])
        label_encoders[col] = le

# Ensure all remaining non-numeric columns are converted to numeric
X = data.drop(columns=['PassesQC'])  # Define X before using it
for col in X.select_dtypes(include=['object']).columns:
    X[col] = LabelEncoder().fit_transform(X[col])

# Set the target variable for classification
y = data['PassesQC']  # Binary target variable

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest Classifier
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))

# UI Mapping
def map_ui_input_to_model(input_data):
    """
    Maps UI input data to the format expected by the model.
    :param input_data: Dictionary containing input data from the UI.
    :return: Processed DataFrame ready for prediction.
    """
    input_df = pd.DataFrame([input_data])
    
    # Apply label encoding for categorical columns
    for col, le in label_encoders.items():
        if col in input_df.columns:
            try:
                input_df[col] = le.transform(input_df[col])
            except ValueError:
                # Handle unseen categories
                input_df[col] = input_df[col].apply(lambda x: -1 if x not in le.classes_ else le.transform([x])[0])
    
    # Ensure all remaining non-numeric columns are converted to numeric
    for col in input_df.select_dtypes(include=['object']).columns:
        raise ValueError(f"Unexpected non-numeric column '{col}' in input data.")
    
    return input_df

def predict_from_ui(input_data):
    """
    Predicts whether the gene is functional based on UI input.
    :param input_data: Dictionary containing input data from the UI.
    :return: Predicted value (Functional or Not Functional).
    """
    try:
        processed_input = map_ui_input_to_model(input_data)
        prediction = model.predict(processed_input)[0]
        return "Functional" if prediction == 1 else "Not Functional"
    except Exception as e:
        raise ValueError(f"Error during prediction: {e}")