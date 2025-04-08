from flask import Blueprint, request, jsonify, g
from flask_restful import Api, Resource
from model.match_score import MatchScore
from api.jwt_authorize import token_required

match_score_api = Blueprint('match_score_api', __name__, url_prefix='/api')
api = Api(match_score_api)

class _MatchScore(Resource):
    @token_required()
    def post(self):
        """Receive and store score from frontend"""
        current_user = g.current_user
        data = request.get_json()

        try:
            score = MatchScore(
                user_id=current_user.id,
                username=current_user.name,
                correct_matches=int(data['correct_matches']),
                gc_stability=int(data['gc_stability'])
            )
            score.create()
            return {"message": "Score recorded", "score": score.read()}, 201
        except Exception as e:
            return {"message": "Failed to save score", "error": str(e)}, 500

    @token_required()
    def get(self):
        """Get all match scores"""
        try:
            scores = MatchScore.query.order_by(MatchScore.created_at.desc()).all()
            return [score.read() for score in scores], 200
        except Exception as e:
            return {"message": "Failed to retrieve scores", "error": str(e)}, 500

api.add_resource(_MatchScore, '/match-score')
