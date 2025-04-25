from flask import Blueprint, request, jsonify, current_app, g
from flask_restful import Api, Resource
from api.jwt_authorize import token_required
from model.editing import predict_functionality

editing_api = Blueprint('editing_api', __name__, url_prefix='/api')
api = Api(editing_api)

class EditingAPI:
    class _Predict(Resource):
        @token_required()
        def post(self):
            current_user = g.current_user
            body = request.get_json()
            input_data = body.get('input_data')

            if input_data is None or not isinstance(input_data, dict):
                return {'message': 'Invalid input data provided'}, 400

            try:
                prediction = predict_functionality(input_data)
                return jsonify({'message': 'Prediction successful', 'prediction': prediction})
            except Exception as e:
                current_app.logger.error(f"Prediction error: {str(e)}")
                return {'message': 'Prediction failed', 'error': str(e)}, 500

api.add_resource(EditingAPI._Predict, '/editing')