from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from init import db

class MatchScore(db.Model):
    __tablename__ = 'match_scores'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    username = Column(String(120), nullable=False)
    correct_matches = Column(Integer, nullable=False)
    gc_stability = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, user_id, username, correct_matches, gc_stability):
        self.user_id = user_id
        self.username = username
        self.correct_matches = correct_matches
        self.gc_stability = gc_stability

    def create(self):
        db.session.add(self)
        db.session.commit()

    def read(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "correct_matches": self.correct_matches,
            "gc_stability": self.gc_stability,
            "created_at": self.created_at.isoformat()
        }
