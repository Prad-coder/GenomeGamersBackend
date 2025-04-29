import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import os

# Load dataset
data_path = os.path.join(os.path.dirname(__file__), '..', 'us_state_vaccinations.csv')
data = pd.read_csv(data_path)

# Drop missing values
data = data.dropna(subset=['total_vaccinations', 'total_distributed', 'people_vaccinated', 'daily_vaccinations'])

# Engineer a feature
data['vacc_rate'] = data['people_vaccinated'] / (data['total_distributed'] + 1)

# Define risk levels (same as before)
def classify_risk(row):
    if row['vacc_rate'] > 0.7:
        return 'low'
    elif row['vacc_rate'] > 0.5:
        return 'moderate'
    elif row['vacc_rate'] > 0.3:
        return 'high'
    else:
        return 'extreme'

data['RiskLevel'] = data.apply(classify_risk, axis=1)

# Encode categorical target
label_encoder = LabelEncoder()
data['RiskLevel_encoded'] = label_encoder.fit_transform(data['RiskLevel'])

# Select features and target
X = data[['total_vaccinations', 'people_vaccinated', 'daily_vaccinations', 'vacc_rate']]
y = data['RiskLevel_encoded']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(random_state=42, class_weight='balanced')
model.fit(X_train, y_train)

# Prediction interface
def predict_risk(input_data: dict):
    input_df = pd.DataFrame([input_data])

    # Feature engineering (vacc_rate must be created for new input)
    input_df['vacc_rate'] = input_df['people_vaccinated'] / (input_df['total_distributed'] + 1)

    # Make sure all columns exist
    required_cols = ['total_vaccinations', 'people_vaccinated', 'daily_vaccinations', 'vacc_rate']
    missing_cols = [col for col in required_cols if col not in input_df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns in input data: {missing_cols}")

    prediction = model.predict(input_df[required_cols])[0]

    # Map encoded output back to readable label
    risk_labels = label_encoder.inverse_transform([prediction])[0]
    return risk_labels