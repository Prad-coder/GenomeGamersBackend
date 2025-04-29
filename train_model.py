import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from joblib import dump

# Load dataset
df = pd.read_csv('data/us_state_vaccinations.csv')

# Fill missing values
df.fillna(0, inplace=True)

# Example engineered feature: vaccination rate
df['vacc_rate'] = df['people_fully_vaccinated'] / (df['total_distributed'] + 1)

# Define target
def classify_risk(row):
    if row['vacc_rate'] > 0.7:
        return 'low'
    elif row['vacc_rate'] > 0.5:
        return 'moderate'
    elif row['vacc_rate'] > 0.3:
        return 'high'
    else:
        return 'extreme'

df['risk'] = df.apply(classify_risk, axis=1)

# Select features and target
features = ['total_vaccinations', 'people_fully_vaccinated', 'daily_vaccinations', 'vacc_rate']
X = df[features]
y = LabelEncoder().fit_transform(df['risk'])

# Train model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Save model
dump(model, 'model/outbreak_model.pkl')
print("✅ Model trained and saved as outbreak_model.pkl")