from app import create_app
from database import db
from models import User

app = create_app()
with app.app_context():
    u = User.query.filter_by(username='shine').first()
    if u:
        print('shine already exists')
    else:
        u = User(username='shine', email='admin@college.edu', role='admin')
        u.set_password('262425')
        db.session.add(u)
        db.session.commit()
        print('created shine admin')
