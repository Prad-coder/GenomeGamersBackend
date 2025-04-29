import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import os

# Load dataset
data_path = os.path.join(os.path.dirname(__file__), '..', 'dna_mutations.csv')
data = pd.read_csv(data_path)

# Drop 'Position' if not needed
data = data.drop(columns=['Position'], errors='ignore')

# Define biological impact scores
bio_impact_map = {
    'Silent Substitution': 0.0,
    'Missense Substitution': 0.5,
    'In-Frame Deletion': 0.6,
    'In-Frame Insertion': 0.6,
    'Frame-Shift Insertion': 1.0,
    'Nonsense Substitution': 1.0,
    'Read-through Substitution': 0.8
}

# Apply biological impact scores
data['Bio_Impact'] = data['Mutation_Type'].map(bio_impact_map)
data['Classification'] = data['Bio_Impact'].apply(lambda x: 0 if x == 0.0 else 1)
data = data.dropna(subset=['Reference_Codon', 'Query_Codon', 'Mutation_Type', 'Bio_Impact', 'Classification'])

# Encode features
label_encoders = {}
for col in ['Reference_Codon', 'Query_Codon', 'Mutation_Type']:
    le = LabelEncoder()
    data[col] = le.fit_transform(data[col])
    label_encoders[col] = le

# Prepare features and target
X = data[['Reference_Codon', 'Query_Codon', 'Mutation_Type', 'Bio_Impact']]
y = data['Classification']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier(random_state=42, class_weight='balanced')
model.fit(X_train, y_train)

# Helper: Map severity
def map_severity(bio_impact):
    if bio_impact == 0.0:
        return "Neutral"
    elif 0 < bio_impact <= 0.5:
        return "Mildly Harmful"
    elif 0.5 < bio_impact <= 0.7:
        return "Moderately Harmful"
    elif 0.7 < bio_impact <= 0.9:
        return "Highly Harmful"
    else:
        return "Severely Harmful"

# Prediction function
def predict_functionality(input_data: dict):
    input_df = pd.DataFrame([input_data])

    for col in ['Reference_Codon', 'Query_Codon', 'Mutation_Type']:
        le = label_encoders.get(col)
        if le:
            try:
                input_df[col] = le.transform(input_df[col])
            except ValueError:
                input_df[col] = input_df[col].apply(
                    lambda x: -1 if x not in le.classes_ else le.transform([x])[0]
                )

    mutation_type = input_data.get('Mutation_Type')
    bio_impact = bio_impact_map.get(mutation_type, 0.5)
    input_df['Bio_Impact'] = bio_impact

    prediction = model.predict(input_df[['Reference_Codon', 'Query_Codon', 'Mutation_Type', 'Bio_Impact']])[0]

    if prediction == 1:
        severity = map_severity(bio_impact)
        return f"Harmful: {severity}"
    else:
        return "Neutral"