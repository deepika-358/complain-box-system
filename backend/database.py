from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Initialize database and seed default data."""
    db.init_app(app)
    with app.app_context():
        # Import models here so SQLAlchemy registers all tables before create_all
        try:
            import backend.models  # noqa: F401
        except ImportError:
            import models  # noqa: F401
        db.create_all()
        _seed_data()


def _seed_data():
    try:
        from backend.models import Category, User
    except ImportError:
        from models import Category, User

    # Seed categories if empty
    if Category.query.count() == 0:
        categories = [
            Category(name="Maintenance",      responsible_email="maintenance@college.edu", color="#f59e0b"),
            Category(name="Academics",        responsible_email="academics@college.edu",   color="#6366f1"),
            Category(name="Administration",   responsible_email="admin@college.edu",        color="#ec4899"),
            Category(name="Hostel",           responsible_email="hostel@college.edu",       color="#14b8a6"),
            Category(name="Transportation",   responsible_email="transport@college.edu",    color="#f97316"),
            Category(name="Canteen / Food",   responsible_email="canteen@college.edu",      color="#84cc16"),
            Category(name="Library",          responsible_email="library@college.edu",      color="#8b5cf6"),
            Category(name="IT / Network",     responsible_email="it@college.edu",           color="#06b6d4"),
            Category(name="Other",            responsible_email="general@college.edu",      color="#6b7280"),
        ]
        db.session.add_all(categories)

    # Seed default admin if empty
    if User.query.count() == 0:
        admin = User(username="shine", email="admin@college.edu", role="admin")
        admin.set_password("262425")
        db.session.add(admin)

    db.session.commit()
    print("[OK] Database seeded successfully.")
