from flask import Blueprint, request, jsonify, current_app, g
from flask_restful import Api, Resource  # used for REST API building
from api.jwt_authorize import token_required
from model.editing import model

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
            print("Request Body:", body)  # Add this

            # Validate input data
            input_data = body.get('input_data')
            if input_data is None or not isinstance(input_data, dict):
                return {'message': 'Invalid input data provided'}, 400

            try:
                # Preprocess input_data to match the expected format
                processed_data = self._preprocess_input(input_data)

                # Reshape the processed data into a 2D array
                reshaped_data = [processed_data]  # Convert to 2D array (1 sample, n features)

                # Perform prediction using the ML model
                prediction = model.predict(reshaped_data)

                # Convert prediction to a JSON-serializable format
                prediction_list = prediction.tolist()  # Convert ndarray to list

                return jsonify({'message': 'Prediction successful', 'prediction': prediction_list})
            except Exception as e:
                current_app.logger.error(f"Error during prediction: {str(e)}")
                return {'message': 'Failed to make prediction', 'error': str(e)}, 500

        def _preprocess_input(self, input_data):
            """
            Preprocess the input data to match the expected format for the model.
            """
            # Convert dict values to a list of floats, skipping invalid values
            processed_data = []
            for key, value in input_data.items():
                try:
                    processed_data.append(float(value))
                except ValueError:
                    current_app.logger.warning(f"Skipping invalid value for key '{key}': '{value}' is not a valid number")
            
            # Ensure the processed data has the required number of features (6)
            required_features = 6
            if len(processed_data) < required_features:
                processed_data.extend([0.0] * (required_features - len(processed_data)))
            elif len(processed_data) > required_features:
                processed_data = processed_data[:required_features]

            if not processed_data:
                raise ValueError("No valid numeric data found in input")
            return processed_data

# Register the API resources with the Blueprint
api.add_resource(EditingAPI._Predict, '/editing')