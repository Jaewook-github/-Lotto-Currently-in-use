import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lotto.db')