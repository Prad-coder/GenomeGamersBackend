from flask import Blueprint, request, jsonify
from model.outbreak import predict_risk

predict_blueprint = Blueprint('predict', __name__)

@predict_blueprint.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        # Extract necessary fields
        vaccines = data.get('vaccines')
        fully_vaccinated = data.get('fully_vaccinated')
        daily_vaccinations = data.get('daily_vaccinations')
        distributed = data.get('distributed')

        # Validate inputs
        if not all([vaccines, fully_vaccinated, daily_vaccinations, distributed]):
            return jsonify({'error': 'Missing parameters'}), 400

        # Prepare input data for prediction
        input_data = {
            'total_vaccinations': vaccines,
            'people_vaccinated': fully_vaccinated,
            'daily_vaccinations': daily_vaccinations,
            'total_distributed': distributed
        }

        # Predict using the live model
        risk = predict_risk(input_data)

        return jsonify({'risk': risk})

    except Exception as e:
        return jsonify({'error': str(e)}), 500