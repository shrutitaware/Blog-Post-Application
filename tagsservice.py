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
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@auth.verify_password
def verify(username, password):
    db = get_db()
    c = db.cursor()
    message = {}
    try:
        c.execute("select password from users where email=(:email)", {'email':username})
        row = c.fetchone()
        if row is not None:
            p = row[0]
            if (sha256_crypt.verify(password,p)):
                return True
            else:
                message = {
                    'status': 201,
                    'mesg': 'Password does not match: ' + request.url,
                }
                return False
        else:
            message = {
                'status': 201,
                'mesg': 'User does not match: ' + request.url,
            }
            return False

    except sqlite3.Error as er:
        print(er)

    return False

# Add new tags
@app.route("/tag/addtag", methods=['POST'])
@auth.login_required
def addTags():
    if (request.method == 'POST'):
        db = get_db()
        c = db.cursor()
        details = request.get_json()
        update_time = datetime.datetime.now()
        email = request.authorization.username

        try:
            
            tag_Details=details['tag'].split(',')
            articleId=details['articleId']
            c.execute("SELECT article_id FROM article WHERE article_id=?",(articleId,))
            rec=c.fetchone()
            #datalen=len(rec)
            if (rec):
                for tags in tag_Details:
                    tag=tags.strip()
                    c.execute("SELECT tag_id FROM tag_head WHERE tag_name=?",(tag,))
                    rec=c.fetchall()
                    rowsaffected=len(rec) 
                    if rowsaffected == 0:
                        c.execute("INSERT INTO tag_head (tag_name,create_time,update_time) VALUES (?,?,?)",(tag,datetime.datetime.now(), datetime.datetime.now()))
                        c.execute("SELECT tag_id FROM tag_head WHERE tag_name=?",(tag,))
                        rec2=c.fetchall()
                        tid=rec2[0][0]
                        c.execute("INSERT INTO tag_detail (article_id,tag_id,create_time,update_time) VALUES (?,?,?,?)",(articleId,tid,datetime.datetime.now(), datetime.datetime.now()))
                    else:
                        tid=rec[0][0]
                        c.execute("INSERT INTO tag_detail VALUES (?,?,?,?)",(articleId,tid,datetime.datetime.now(), datetime.datetime.now()))

                    if (c.rowcount == 1):
                        db.commit()
                        response = Response(status=201, mimetype='application/json')

                    else:
                        response = Response(status=404, mimetype='application/json')
            else:
                response = Response(status=409, mimetype='application/json')            

        except sqlite3.Error as er:
            print(er)
            response = Response(status=409, mimetype='application/json')

        return response    


#Delete a tag

@app.route("/tag/deletetag", methods=['DELETE'])
@auth.login_required
def deletetag():
    if (request.method == 'DELETE'):
        try:
            db = get_db()
            c = db.cursor()
            details = request.get_json()
            artid= details['articleId']
            tag=details['tag']
            c.execute("DELETE FROM tag_detail WHERE article_id=? AND tag_id IN (SELECT tag_id FROM tag_head WHERE tag_name=?)",(artid,str(tag),))
            db.commit()
            if (c.rowcount == 1):
                db.commit()
                response = Response(status=200, mimetype='application/json')
            else:
                response = Response(status=404, mimetype='application/json')
        except sqlite3.Error as er:
                print(er)
                response = Response(status=409, mimetype='application/json')

    return response
#get all the tags related to article by article ID
@app.route("/tag/gettag/<artid>", methods=['GET'])
def getarticle(artid):
    if (request.method == 'GET'):
        try:
            db = get_db()
            db.row_factory = dict_factory
            c = db.cursor()
            c.execute("SELECT * FROM tag_head WHERE tag_id IN (SELECT tag_id FROM tag_detail WHERE article_id=?)",(artid,))
            row = c.fetchall()
            db.commit()
            if row is not None:
                return jsonify(row)
            else:
                response = Response(status=404, mimetype='application/json')

        except sqlite3.Error as er:
                print(er)
                response = Response(status=409, mimetype='application/json')

    return response

# get all the articles with the given tag
@app.route('/tag/getarticles/<tag>',methods=['GET'])
def getart(tag):
    try:
        db = get_db()
        db.row_factory = dict_factory
        c = db.cursor()
        c.execute("SELECT article_id FROM tag_detail WHERE tag_id IN (SELECT tag_id FROM tag_head WHERE tag_name=?)",(tag,))
        row = c.fetchall()
        db.commit()
        if row is not None:
            return jsonify(row)
        else:
            response = Response(status=404, mimetype='application/json')

    except sqlite3.Error as er:
            print(er)
            response = Response(status=409, mimetype='application/json')

    return response    

if __name__ == '__main__':
    app.run(debug=True)
