import os
from pathlib import Path
from flask import Flask, jsonify
from flask_login import LoginManager
from backend.config import config_by_name
from backend.app.database import db

login_manager = LoginManager()


def create_app(config_name=None):
    """Application Factory Pattern"""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    # Set template and static folders explicitly relative to project root
    root_dir = Path(__file__).resolve().parent.parent.parent
    template_dir = root_dir / "frontend" / "templates"
    static_dir = root_dir / "frontend" / "static"

    app = Flask(
        __name__,
        template_folder=str(template_dir),
        static_folder=str(static_dir),
    )

    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    # User loader callback for Flask-Login
    from backend.app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from flask import request

    @login_manager.unauthorized_handler
    def unauthorized():
        if request.is_json or request.path.startswith("/api/"):
            return jsonify({"error": "Unauthorized access. Authentication required."}), 401
        return redirect(url_for("auth.login"))

    # Register blueprints (routes will be imported once defined in later phases)
    register_blueprints(app)

    # Global security response headers
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    # Global Health Check API Endpoint
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify(
            {
                "status": "healthy",
                "service": "AI-Based Network Intrusion Detection System",
                "version": "1.0.0",
            }
        ), 200

    # Ensure DB tables exist and default seed user exists
    with app.app_context():
        db.create_all()
        seed_default_users()

    return app


def register_blueprints(app):
    """Register all application route blueprints"""
    from backend.app.routes.auth_routes import auth_bp
    from backend.app.routes.predict import predict_bp
    from backend.app.routes.dashboard import dashboard_bp
    from backend.app.routes.alerts import alerts_bp
    from backend.app.routes.reports import reports_bp
    from backend.app.routes.model_metrics import metrics_bp
    from backend.app.routes.views import views_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(predict_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(metrics_bp)
    app.register_blueprint(views_bp)


def seed_default_users():
    """Seed initial default admin and analyst users if empty"""
    from backend.app.models.user import User

    if not User.query.first():
        admin = User(
            username="admin",
            email="admin@nids.local",
            role="Admin",
        )
        admin.set_password("Admin@123456")

        analyst = User(
            username="analyst",
            email="analyst@nids.local",
            role="Analyst",
        )
        analyst.set_password("Analyst@123456")

        db.session.add(admin)
        db.session.add(analyst)
        db.session.commit()
        print("[+] Default seed users initialized: admin (Admin@123456), analyst (Analyst@123456)")
