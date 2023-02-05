import sqlite3

from flask import Flask, request, g, render_template, send_file

DATABASE = 'example.db'
db = None
def connect_to_database():
    # return sqlite3.connect(app.config['DATABASE'])
    return sqlite3.connect(DATABASE)

def get_db():
    global db
    if db is None:
        db =connect_to_database()
    return db

def close_connection(exception=None):
    if db is not None:
        db.close()

def execute_query(query, args=(), connect=False):
    global db
    db = get_db()
    cur = db.execute(query, args)
    if connect:
        db.commit()
    rows = cur.fetchall()
    cur.close()
    return rows
execute_query("DROP TABLE IF EXISTS users")
execute_query("CREATE TABLE users (Username text,Password text,firstname text, lastname text, email text, count integer, filename text, filecontent text)", (),True)
close_connection()

