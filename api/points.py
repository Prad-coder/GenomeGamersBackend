import jwt
from flask import Blueprint, request, jsonify, current_app, Response, g
from flask_restful import Api, Resource  # used for REST API building
from datetime import datetime
from __init__ import app
from api.jwt_authorize import token_required
from model.points import Points

# Create a Blueprint for the points API
points_api = Blueprint('points_api', __name__, url_prefix='/api')

# Create an Api object and associate it with the Blueprint
api = Api(points_api)

class PointsAPI:
    class _Points(Resource):
        """
        API operations for managing points entries.
        """

        @token_required()
        def post(self):
            """
            Add a new points entry for the authenticated user.
            """
            current_user = g.current_user
            body = request.get_json()

            # Validate points
            points = body.get('points')
            if points is None or not isinstance(points, int) or points < 0:
                return {'message': 'Invalid points provided'}, 400

            try:
                # Ensure no existing entry exists
                existing_points = Points.query.filter_by(user=current_user.uid).first()
                if existing_points:
                    return {'message': 'Points entry already exists'}, 400

                # Create a new points entry
                new_points = Points(user=current_user.uid, points=points)
                new_points.create()
                return jsonify({'message': 'Points added successfully', 'points': new_points.read()})
            except Exception as e:
                return {'message': 'Failed to create points', 'error': str(e)}, 500

        @token_required()
        def put(self):
            """
            Update an existing points entry for the authenticated user.
            """
            current_user = g.current_user
            body = request.get_json()

            # Validate points
            points = body.get('points')
            if points is None or not isinstance(points, int) or points < 0:
                return {'message': 'Invalid points provided'}, 400

            try:
                # Fetch and update the user's points entry
                points_entry = Points.query.filter_by(user=current_user.uid).first()
                if not points_entry:
                    return {'message': 'No points entry found to update'}, 404

                points_entry.points = points
                points_entry.create()  # Save changes to the database
                return jsonify({'message': 'Points updated successfully', 'points': points_entry.read()})
            except Exception as e:
                return {'message': 'Failed to update points', 'error': str(e)}, 500

        @token_required()
        def get(self):
            """
            Get the current user's points entry.
            """
            current_user = g.current_user

            try:
                current_app.logger.debug(f"Fetching points for user: {current_user.uid}")
                points_entry = Points.query.filter_by(user=current_user.uid).first()
                if points_entry:
                    current_app.logger.debug(f"Points entry found: {points_entry.read()}")
                    return jsonify({'message': 'Points retrieved successfully', 'points': points_entry.read()})
                else:
                    current_app.logger.debug("No points entry found for the user")
                    return {'message': 'No points entry found for the user'}, 404
            except Exception as e:
                current_app.logger.error(f"Error retrieving points: {str(e)}")
                return {'message': 'Failed to retrieve points', 'error': str(e)}, 500

        @token_required()
        def delete(self):
            """
            Delete an existing points entry for the authenticated user.
            """
            current_user = g.current_user

            try:
                # Fetch and delete the user's points entry
                points_entry = Points.query.filter_by(user=current_user.uid).first()
                if not points_entry:
                    return {'message': 'No points entry found to delete'}, 404

                points_entry.delete()  # Delete the entry from the database
                return jsonify({'message': 'Points entry deleted successfully'})
            except Exception as e:
                return {'message': 'Failed to delete points entry', 'error': str(e)}, 500

# Register the API resources with the Blueprint
api.add_resource(PointsAPI._Points, '/points')