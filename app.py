from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:your_password@localhost/fitness_center_db'
db = SQLAlchemy(app)

class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    workouts = db.relationship('WorkoutSession', backref='member', lazy=True)

class WorkoutSession(db.Model):
    __tablename__ = 'workout_sessions'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Integer, nullable=False) 
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)

with app.app_context():
    db.create_all()  

@app.route('/members', methods=['POST'])
def add_member():
    data = request.get_json()
    new_member = Member(name=data['name'], email=data['email'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({'message': 'Member added', 'id': new_member.id}), 201

@app.route('/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    return jsonify([{'id': member.id, 'name': member.name, 'email': member.email} for member in members]), 200

@app.route('/members/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    member = Member.query.get_or_404(member_id)
    data = request.get_json()
    member.name = data.get('name', member.name)
    member.email = data.get('email', member.email)
    db.session.commit()
    return jsonify({'message': 'Member updated'}), 200

@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    member = Member.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({'message': 'Member deleted'}), 200

@app.route('/workout_sessions', methods=['POST'])
def add_workout_session():
    data = request.get_json()
    new_session = WorkoutSession(date=data['date'], duration=data['duration'], member_id=data['member_id'])
    db.session.add(new_session)
    db.session.commit()
    return jsonify({'message': 'Workout session added', 'id': new_session.id}), 201

@app.route('/workout_sessions', methods=['GET'])
def get_workout_sessions():
    sessions = WorkoutSession.query.all()
    return jsonify([{'id': session.id, 'date': session.date.isoformat(), 'duration': session.duration, 'member_id': session.member_id} for session in sessions]), 200

@app.route('/members/<int:member_id>/workout_sessions', methods=['GET'])
def get_member_workout_sessions(member_id):
    sessions = WorkoutSession.query.filter_by(member_id=member_id).all()
    return jsonify([{'id': session.id, 'date': session.date.isoformat(), 'duration': session.duration} for session in sessions]), 200

if __name__ == '__main__':
    app.run(debug=True)