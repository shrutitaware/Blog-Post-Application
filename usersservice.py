from flask import Flask, jsonify, request, Response, g
import sqlite3, json
from flask_api import status
import datetime
from http import HTTPStatus
from flask_httpauth import HTTPBasicAuth
from passlib.hash import sha256_crypt

app = Flask(__name__)
auth = HTTPBasicAuth()

DATABASE = 'blogdatabase.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.cursor().execute("PRAGMA foreign_keys = ON")
        db.commit()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        print("database closed")
        db.close()

@app.route("/createuser", methods=['POST'])
def createuser():
    if (request.method == 'POST'):
        try:
            details = request.get_json()
            db = get_db()
            c = db.cursor()
            update_time = datetime.datetime.now()

            password = sha256_crypt.encrypt((str(details['password'])))
            c.execute("insert into users (name, email, password, create_time, update_time) values (?,?,?,?,?)",
                    [details['name'], details['email'], password, update_time, update_time ])
            db.commit()

            response = Response(status=201, mimetype='application/json')

        except sqlite3.Error as er:
            print(er)
            response = Response(status=409, mimetype='application/json')

    return response

@auth.verify_password
def verify(username, password):
    print("inside verify")
    try:
        db = get_db()
        c = db.cursor()
        message = {}

        c.execute("select password from users where email=(:email)", {'email':username})
        row = c.fetchone()
        if row is not None:
            p = row[0]
            print(p)
            if (sha256_crypt.verify(password,p)):
                return True
            else:
                return False
        else:
            return False

    except sqlite3.Error as er:
        print(er)

    return False

@app.route("/display", methods=['POST'])
def display():
    db = get_db()
    c = db.cursor()
    message = {}
    c.execute("select * from users")
    row = c.fetchall()

    #row = c.execute("select * from users")
    '''
    message = {
        'status': 201,
        'test': 'works fine: ' + request.url,
    }
    '''

    return jsonify(row)

@app.route("/deleteuser", methods=['DELETE'])
@auth.login_required
def deleteuser():
    try:
        db = get_db()
        c = db.cursor()
        email = request.authorization.username

        c.execute("delete from users where email=(:email)",{'email':email})
        db.commit()

        response = Response(status=200, mimetype='application/json')

    except sqlite3.Error as er:
            print(er)
            response = Response(status=409, mimetype='application/json')

    return response

@app.route("/updatepassword", methods=['PATCH'])
@auth.login_required
def updatepassword():
    try:
        db = get_db()
        c = db.cursor()
        details = request.get_json()
        new_password = sha256_crypt.encrypt((str(details['new_password'])))
        email = request.authorization.username
        update_time = datetime.datetime.now()

        c.execute("update users set password=(:password), update_time=(:updatetime) where email=(:email)",{'email':email, 'password':new_password, 'updatetime':update_time})
        db.commit()
        response = Response(status=200, mimetype='application/json')

    except sqlite3.Error as er:
        print(er)
        response = Response(status=409, mimetype='application/json')

    return response

if __name__ == '__main__':
    app.run(debug=True)
