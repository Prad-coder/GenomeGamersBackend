from flask import Blueprint, request, jsonify
from joblib import load
import numpy as np

predict_blueprint = Blueprint('predict', __name__)

# Load your real ML model
model = load('models/outbreak_model.pkl')

@predict_blueprint.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        vaccines = data.get('vaccines')
        fully_vaccinated = data.get('fully_vaccinated')
        daily_vaccinations = data.get('daily_vaccinations')
        distributed = data.get('distributed')

        if not all([vaccines, fully_vaccinated, daily_vaccinations, distributed]):
            return jsonify({'error': 'Missing parameters'}), 400

        # Create features same as during training
        vacc_rate = fully_vaccinated / (distributed + 1)
        features = np.array([[vaccines, fully_vaccinated, daily_vaccinations, vacc_rate]])

        prediction = model.predict(features)[0]

        risk_levels = ['low', 'moderate', 'high', 'extreme']  # must match order from your label encoder
        risk = risk_levels[prediction]

        return jsonify({'risk': risk})

    except Exception as e:
        return jsonify({'error': str(e)}), 500