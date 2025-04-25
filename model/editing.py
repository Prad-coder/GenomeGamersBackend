import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import os

# Load dataset
data_path = os.path.join(os.path.dirname(__file__), '..', 'gene_editing.csv')
data = pd.read_csv(data_path)

# Drop unnecessary columns if they exist
data = data.drop(columns=['SequenceID', 'ScreenID', 'Replicate', 'Library', 'ModelConditionID'], errors='ignore')

# Drop missing
data = data.dropna(subset=['PassesQC', 'ExcludeFromCRISPRCombined'])

# Encode categorical columns
label_encoders = {}
categorical_columns = ['ScreenType', 'DrugTreated']
for col in categorical_columns:
    if col in data.columns:
        le = LabelEncoder()
        data[col] = le.fit_transform(data[col])
        label_encoders[col] = le

# Catch any object dtypes and encode
X = data.drop(columns=['PassesQC'])
for col in X.select_dtypes(include=['object']).columns:
    le = LabelEncoder()
    data[col] = le.fit_transform(data[col])
    label_encoders[col] = le

# Remove explicit encoding of target variable (PassesQC)
# Final feature/target split
X = data.drop(columns=['PassesQC'])
y = data['PassesQC']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(random_state=42, class_weight='balanced')
model.fit(X_train, y_train)

# Prediction interface
def predict_functionality(input_data: dict):
    input_df = pd.DataFrame([input_data])

    # Apply all encoders
    for col, le in label_encoders.items():
        if col in input_df.columns:
            try:
                input_df[col] = le.transform(input_df[col])
            except ValueError:
                input_df[col] = input_df[col].apply(lambda x: -1 if x not in le.classes_ else le.transform([x])[0])

    # Encode any remaining object columns
    for col in input_df.select_dtypes(include=['object']).columns:
        raise ValueError(f"Unexpected non-numeric column '{col}' in input data.")

    prediction = model.predict(input_df)[0]
    return "Functional" if prediction == 1 else "Not Functional"