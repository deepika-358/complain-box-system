from database import db
from models import User
from app import create_app

app = create_app()
with app.app_context():
    users = User.query.all()
    for u in users:
        print(f"id={u.id}, username={u.username}, email={u.email}, role={u.role}, pw_hash={u.password_hash[:30]}...")
