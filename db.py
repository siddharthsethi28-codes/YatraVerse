import os
from flask_mysqldb import MySQL

mysql = MySQL()

def init_db(app):
    app.config['MYSQL_HOST']     = os.getenv('DB_HOST', 'localhost')
    app.config['MYSQL_PORT']     = int(os.getenv('DB_PORT', 3306))
    app.config['MYSQL_USER']     = os.getenv('DB_USER', 'root')
    app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD', '')
    app.config['MYSQL_DB']       = os.getenv('DB_NAME', 'wanderhub_db')
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    mysql.init_app(app)
    return mysql
