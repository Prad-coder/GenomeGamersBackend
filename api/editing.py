from flask import Blueprint, request, jsonify, current_app, g
from flask_restful import Api, Resource  # used for REST API building
from api.jwt_authorize import token_required
from model.editing import model, map_ui_input_to_model  # Ensure both are imported

# Create a Blueprint for the editing API
editing_api = Blueprint('editing_api', __name__, url_prefix='/api')

# Create an Api object and associate it with the Blueprint
api = Api(editing_api)

class EditingAPI:
    class _Predict(Resource):
        """
        API operations for ML model predictions.
        """

        @token_required()
        def post(self):
            """
            Use the ML model to make predictions based on the provided input data.
            """
            current_user = g.current_user
            body = request.get_json()
            print("Request Body:", body)

            # Validate input data
            input_data = body.get('input_data')
            if input_data is None or not isinstance(input_data, dict):
                return {'message': 'Invalid input data provided'}, 400

            try:
                # Preprocess input using map_ui_input_to_model from your ML model file
                processed_df = map_ui_input_to_model(input_data)

                # Perform prediction using the trained model
                prediction = model.predict(processed_df)[0]

                # Format the prediction
                readable_prediction = "Functional" if prediction == 1 else "Not Functional"

                return jsonify({'message': 'Prediction successful', 'prediction': readable_prediction})

            except Exception as e:
                current_app.logger.error(f"Error during prediction: {str(e)}")
                return {'message': 'Failed to make prediction', 'error': str(e)}, 500

# Register the API resources with the Blueprint
api.add_resource(EditingAPI._Predict, '/editing')