from sqlalchemy import Integer
from __init__ import app, db

class Points(db.Model):
    """
    Points Model
    
    The Points class represents the total points data for a user.
    
    Attributes:
        id (db.Column): The primary key, an integer representing the unique identifier for the record.
        user (db.Column): A string representing the username associated with the points.
        points (db.Column): An integer representing the total points earned by the user.
    """
    __tablename__ = 'points'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(255), nullable=False, unique=True)  # Ensure one entry per user
    points = db.Column(db.Integer, nullable=False)

    def __init__(self, user, points):
        """
        Constructor, initializes a Points object.
        
        Args:
            user (str): The username associated with the points.
            points (int): The total points earned by the user.
        """
        self.user = user
        self.points = points

    def __repr__(self):
        """
        The __repr__ method is a special method used to represent the object in a string format.
        Called by the repr() built-in function.
        
        Returns:
            str: A text representation of how to create the object.
        """
        return f"Points(id={self.id}, user={self.user}, points={self.points})"
    
    def create(self):
        """
        The create method adds the object to the database and commits the transaction.
        
        Uses:
            The db ORM methods to add and commit the transaction.
        
        Raises:
            Exception: An error occurred when adding the object to the database.
        """
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def delete(self):
        """
        Deletes the points entry from the database.
        """
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def read(self):
        """
        The read method retrieves the object data from the object's attributes and returns it as a dictionary.
        
        Returns:
            dict: A dictionary containing the points data.
        """
        return {
            'id': self.id,
            'user': self.user,
            'points': self.points
        }

    def update(self):
        """
        Update an existing points entry in the database.
        
        Returns:
            bool: True if the points entry was successfully updated, False otherwise.
        """
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False

    @staticmethod
    def restore(data):
        """
        Restore points from a list of dictionaries, replacing existing entries.

        Args:
            data (list): List of dictionaries containing points data.

        Returns:
            dict: Dictionary of restored Points objects.
        """
        with app.app_context():
            # Clear the existing table
            db.session.query(Points).delete()
            db.session.commit()

            restored_points = {}
            for points_data in data:
                points = Points(
                    user=points_data['user'],
                    points=points_data['points']
                )
                points.create()
                restored_points[points_data['id']] = points

            return restored_points

def initPoints():
    """
    The initPoints function creates the Points table and adds tester data to the table.
    
    Uses:
        The db ORM methods to create the table.
    
    Instantiates:
        Points objects with tester data.
    
    Raises:
        Exception: An error occurred when adding the tester data to the table.
    """
    with app.app_context():
        """Create database and tables"""
        db.create_all()
        """Tester data for table"""
        tester_data = [
            Points(user='user1', points=100),
            Points(user='user2', points=200),
            Points(user='user3', points=300),
            Points(user='niko', points=400)
        ]
        
        for data in tester_data:
            try:
                db.session.add(data)
                db.session.commit()
                print(f"Record created: {repr(data)}")
            except Exception as e:
                db.session.rollback()
                print(f"Error creating record for user {data.user}: {e}")
