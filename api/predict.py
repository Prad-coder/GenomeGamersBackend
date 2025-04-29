from flask import Blueprint, request, jsonify

predict_blueprint = Blueprint('predict', __name__)

# ---- Dummy risk model (for now) ----
def simple_risk_model(vaccines_allocated, region_population):
    coverage = vaccines_allocated / region_population
    if coverage > 0.7:
        return 'low'
    elif coverage > 0.5:
        return 'moderate'
    elif coverage > 0.3:
        return 'high'
    else:
        return 'extreme'

@predict_blueprint.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        region = data.get('region')
        vaccines = data.get('vaccines')
        population = data.get('population')

        if not all([region, vaccines, population]):
            return jsonify({'error': 'Missing parameters'}), 400

        risk_level = simple_risk_model(vaccines, population)
        return jsonify({'region': region, 'risk': risk_level})

    except Exception as e:
        return jsonify({'error': str(e)}), 500