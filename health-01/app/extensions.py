from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize extensions without app context (initialized in create_app)
db = SQLAlchemy()
login_manager = LoginManager()
