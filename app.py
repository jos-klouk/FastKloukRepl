import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
from sqlalchemy.orm import DeclarativeBase
from auth0 import AuthError
from flask_migrate import Migrate
from sqlalchemy import text

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    from routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        response = jsonify(ex.error)
        response.status_code = ex.status_code
        return response

    @app.route('/test-db')
    def test_db():
        try:
            db.session.execute(text('SELECT 1'))
            return 'Database connection successful', 200
        except Exception as e:
            return f'Database connection failed: {str(e)}', 500

    return app
