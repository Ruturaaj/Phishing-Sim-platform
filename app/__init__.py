from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

db = SQLAlchemy()
mail = Mail()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = '733837fce4abd3fd88022b9289411f31983937ee0c6d655d2fddf9da061e25dc'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///phishing_logs.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = 'your_mailtrap_username'
    app.config['MAIL_PASSWORD'] = 'your_mailtrap_password'
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False

    db.init_app(app)
    mail.init_app(app)

    with app.app_context():
        from . import routes
        db.create_all()

    return app
