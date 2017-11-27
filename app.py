import os
import jwt
import traceback
import datetime
from functools import wraps
from werkzeug.utils import secure_filename
from flask import Flask, request, redirect, render_template, jsonify
from flask.ext.bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from models import app, db, User, Paragraph

# app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['secretkey'] = 'some-strong+secret#key'


########################################
#          Token Authentication        #
########################################
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        # ensure that token is specified in the request
        if not token:
            return jsonify({'message': 'Missing token!'})

        # ensure that token is valid
        try:
            data = jwt.decode(token, app.config['secretkey'])
        except:
            return jsonify({'message': 'Invalid token!'})

        return f(*args, **kwargs)

    return decorated


@app.route('/')
def home():
    temp_data = {'title': 'SpeechApp'}
    return render_template('index.html', **temp_data)


@app.route('/user_registration', methods=['POST'])
def user_registration():
    ret = {}
    try:
        id = request.form['id']
        name = request.form['name']
        email = request.form['email']
        pswd = request.form['pswd']
        pw_hash = bcrypt.generate_password_hash(pswd)
        user = User(id, name, email, pw_hash)
        db.session.add(user)
        db.session.commit()
        ret['err'] = 0
        ret['msg'] = 'User Registration successfully!'
    except Exception as exp:
        print 'user_registration() :: Got exception: %s' % exp
        ret['err'] = 1
        ret['msg'] = '%s' % exp
        print(traceback.format_exc())
    return jsonify(ret)


@app.route('/user_login', methods=['POST'])
def user_login():
    ret = {}
    try:
        email = request.form['email']
        pswd = request.form['pswd']
        query = User.query.filter_by(email=email).first()
        password_db = query.password

        # match password
        passw = bcrypt.check_password_hash(password_db, pswd)

        if passw:

            # generate token
            expiry = datetime.datetime.utcnow() + \
                     datetime.timedelta(minutes=30)
            token = jwt.encode({'user': email, 'exp': expiry},
                               app.config['secretkey'], algorithm='HS256')

            ret['success'] = True
            ret['msg'] = 'Login successful'
            ret['token'] = token.decode('UTF-8')
        else:
            ret['msg'] = 'Login failed! Email and Password not match'
            ret['success'] = False

    except Exception as exp:
        print 'user_login() :: Got exception: %s' % exp
        ret['msg'] = '%s' % exp
        ret['err'] = 2
        print(traceback.format_exc())
    return jsonify(ret)


@app.route('/study')
def study():
    read_file = open("study.csv", "r")
    data = read_file.read()
    s = data.split(",")
    text_id = s[0]
    text = s[1]
    paragraph = s[2]
    study = Study(text_id, text, paragraph)
    return 'done'


######################################
#           Upload FILE              #
######################################
dir_path = os.path.dirname(os.path.realpath(__file__))
file_path = '%s/%s' % (dir_path, 'upload')
UPLOAD_FOLDER = file_path
ALLOWED_EXTENSION = set(['txt', 'csv', 'png', 'jpg', 'gif', 'pdf'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() \
                               in ALLOWED_EXTENSION


@app.route('/file', methods=['POST'])
def file():
    prefix = request.base_url[:-len('/file')]
    try:
        csv_file = request.files['pdf']

        if csv_file.filename == '':
            flash('Nop Selectd file')
            return redirect(request.url)
        if csv_file and allowed_file(csv_file.filename):
            filename = secure_filename(csv_file.filename)
            csv_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            csv = '%s/%s' % (file_path, filename)
        save_csv_file_url = '%s/uploads/%s' % (prefix, filename)
    except Exception as exp:
        print 'file() :: Got exception: %s' % exp
        print(traceback.format_exc())

    return 'file upload successfully'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
