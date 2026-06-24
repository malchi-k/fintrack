from flask import Flask
from app.config import Config
from app.extensions import db, migrate, login_manager, bcrypt

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # Регистрация Blueprints
    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.transactions.routes import transactions_bp
    #from app.reports.routes import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transactions_bp)
    #app.register_blueprint(reports_bp)

    # Создаём папку instance, если её нет
    import os
    os.makedirs(app.instance_path, exist_ok=True)

    return app