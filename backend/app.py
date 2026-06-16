import os
import sys
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# Ensure the project root is on sys.path so package imports work
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.config import Config
from backend.database import init_db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    JWTManager(app)

    # Database
    init_db(app)

    # Blueprints
    try:
        from backend.routes.complaints import complaints_bp
        from backend.routes.auth import auth_bp
    except ImportError:
        from routes.complaints import complaints_bp
        from routes.auth import auth_bp

    app.register_blueprint(complaints_bp)
    app.register_blueprint(auth_bp)

    @app.route("/")
    def index():
        return {"message": "Complain Box API is running!", "version": "1.0.0"}

    return app


if __name__ == "__main__":
    app = create_app()
    print("\n" + "="*50)
    print("  [*] Complain Box Backend Running!")
    print("  [*] API: http://localhost:5000")
    print("  [*] Default Admin: shine / 262425")
    print("="*50 + "\n")
    app.run(debug=True, port=5000, host="0.0.0.0")
