from flask import Blueprint, request, jsonify, current_app, g
from flask_restful import Api, Resource
# from api.jwt_authorize import token_required  # Uncomment if you need authentication
from model.outbreak import predict_risk

outbreak_api = Blueprint('outbreak_api', __name__, url_prefix='/api')
api = Api(outbreak_api)

class OutbreakAPI:
    class _Predict(Resource):
        # @token_required()  # Optional if using JWT
        def post(self):
            try:
                body = request.get_json()

                # Extract and validate input
                vaccines = body.get('vaccines')
                fully_vaccinated = body.get('fully_vaccinated')
                daily_vaccinations = body.get('daily_vaccinations')
                distributed = body.get('distributed')

                if not all([vaccines, fully_vaccinated, daily_vaccinations, distributed]):
                    return {'message': 'Missing or invalid input parameters'}, 400

                input_data = {
                    'total_vaccinations': vaccines,
                    'people_vaccinated': fully_vaccinated,
                    'daily_vaccinations': daily_vaccinations,
                    'total_distributed': distributed
                }

                prediction = predict_risk(input_data)
                return jsonify({'message': 'Prediction successful', 'risk': prediction})

            except Exception as e:
                current_app.logger.error(f"[OutbreakAPI] Prediction error: {str(e)}")
                return {'message': 'Prediction failed', 'error': str(e)}, 500

api.add_resource(OutbreakAPI._Predict, '/predict')