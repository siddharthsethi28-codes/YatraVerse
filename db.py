import os
import pymysql
import pymysql.cursors

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'wanderhub_db'),
        cursorclass=pymysql.cursors.DictCursor
    )

def init_db(app):
    # Flask app initialization if needed
    pass
