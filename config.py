import os
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_default_secret_key'  # Don't hardcode your key for production
    SQLALCHEMY_DATABASE_URI = 'sqlite:///blog.db'  # You can change this to any database URI (e.g., PostgreSQL, MySQL)
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # To avoid unnecessary warnings
