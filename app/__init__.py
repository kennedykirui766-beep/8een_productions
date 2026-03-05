from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "admin.login"

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Import models
    from app.models.user import User
    from app.models.reaction import PortfolioActivity

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from app.routes.main_routes import main_bp
    from app.routes.project_routes import project_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.payment_routes import payment_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(project_bp, url_prefix="/projects")
    app.register_blueprint(admin_bp)
    app.register_blueprint(payment_bp)

    # ✅ Global template variables for logo and images
    @app.context_processor
    def inject_site_images():
        return dict(
            logo_url=app.config.get("LOGO_URL"),
            about_image_url=app.config.get("ABOUT_IMAGE_URL"),
            hero_image_url=app.config.get("HERO_IMAGE_URL"),
            short_film_url=app.config.get("SHORT_FILM_URL"),
            track_url=app.config.get("TRACK_URL"),
            brand_url=app.config.get("BRAND_URL")
        )

    return app