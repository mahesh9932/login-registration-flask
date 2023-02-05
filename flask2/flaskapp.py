import sqlite3
from flask import Flask, request, g, render_template, send_file

DATABASE = 'example.db'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_to_database():
    # return sqlite3.connect(app.config['DATABASE'])
    return sqlite3.connect(DATABASE)

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = connect_to_database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def execute_query(query, args=(), connect=False):
    db = get_db()
    cur = db.execute(query, args)
    if connect:
        db.commit()
    rows = cur.fetchall()
    cur.close()
    return rows

def commit():
    get_db().commit()

@app.route("/")
def hello():
    return render_template('index.html')

@app.route('/login', methods =['POST', 'GET'])
def login():
    message = ''
    if request.method == 'POST' and str(request.form['username']) !="" and str(request.form['password']) != "":
        print(request.form)
        username = str(request.form['username'])
        password = str(request.form['password'])
        result = execute_query("""SELECT firstname,lastname,email,count  FROM users WHERE Username  = (?) AND Password = (?)""", (username, password ))
        print('result',result)
        if result:
            for row in result:
                return render_template('details.html', firstName=row[0], lastname = row[1], email = row[2], wordCount = row[3], username=username )
                # return responsePage(row[0], row[1], row[2], row[3])
        else:
            message = 'Invalid Credentials !'
    elif request.method == 'POST':
        message = 'Please enter Credentials'
    return render_template('index.html', message = message)

@app.route('/registration', methods =['GET', 'POST'])
def registration():
    message = ''
    if request.method == 'POST' and str(request.form['username']) !="" and str(request.form['password']) !="" and str(request.form['firstname']) !="" and str(request.form['lastname']) !="" and str(request.form['email']) !="":
        username = str(request.form['username'])
        password = str(request.form['password'])
        firstname = str(request.form['firstname'])
        lastname = str(request.form['lastname'])
        email = str(request.form['email'])
        uploaded_file = request.files['textfile']
        if not uploaded_file:
            filename = null
            word_count = null
        else :
            filename = uploaded_file.filename
            data = uploaded_file.read().decode()
            print(data)
            word_count = getNumberOfWords(data)
        result = execute_query("""SELECT *  FROM users WHERE Username  = (?)""", (username, ))
        if result:
            message = 'User has already registered!'
        else:
            result1 = execute_query("""INSERT INTO users (username, password, firstname, lastname, email, count, filename, filecontent) values (?, ?, ?, ?, ?, ?, ?, ? )""", (username, password, firstname, lastname, email, word_count, str(filename), str(data) ), True)
            commit()
            result2 = execute_query("""SELECT firstname,lastname,email,count  FROM users WHERE Username  = (?) AND Password = (?)""", (username, password ))
            print('result2',result2)
            if result2:
                for row in result2:
                    # return render_template('details.html')
                    return render_template('details.html', firstName=row[0], lastname = row[1], email = row[2], wordCount = row[3], username = username )
    elif request.method == 'POST':
        message = 'Some of the fields are missing!'
    return render_template('registration.html', message = message)

@app.route("/download/<username>")
def download(username):
    print(username)
    result = execute_query("""SELECT *  FROM users WHERE Username  = (?)""", (username, ))
    row = result[0]
    f = open(row[6], 'w')
    f.write(str(row[7]))
    f.close()
    path = row[6]
    return send_file(path, as_attachment=True)

def getNumberOfWords(data):
    # data = file.read()
    words = data.split()
    return str(len(words))

def responsePage(firstname, lastname, email, count):
    return """ First Name :  """ + str(firstname) + """ <br> Last Name : """ + str(lastname) + """ <br> Email : """ + str(email) + """ <br> Word Count : """ + str(count) + """ <br><br> <a href="/download" >Download</a> """

if __name__ == '__main__':
  app.run(debug=True)