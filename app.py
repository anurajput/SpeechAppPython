import os
import jwt
import traceback
import datetime
from functools import wraps
from werkzeug.utils import secure_filename
from flask import Flask, request, redirect, render_template, jsonify
from flask.ext.bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from models import app, db, User, Study

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


@app.route('/index')
def index():
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
        ret['success'] = True
        ret['msg'] = 'User Registration successfully!'
    except Exception as exp:
        print 'user_registration() :: Got exception: %s' % exp
        ret['success'] = False
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


@app.route('/add_study', methods=['POST'])
def add_study():
    prefix = request.base_url[:-len('/add_study')]
    try:
        csv_file = request.files['study_file']

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


@app.route('/study')
def study():

    ret = {}
    try:
        # count the no of lines
        with open('upload/study.csv') as f:
            for i, l in enumerate(f):
                pass
        total_lines = i + 1

        # getting the data from the csv file
        csv_file = open('upload/study.csv', "r")

        line = csv_file.readline()
        cnt = 1
        while cnt < total_lines:

            line = csv_file.readline()
            s = line.split(',')
            id = s[0]
            Paragraph_Number = id
            Paragraph_Text = s[1]
            Date_of_Upload = s[2]
            Paragraph_Type = s[3]
            Word_Count = s[4]
            Status = s[5]
            GCS_Output = s[6]
            GCS_Acc = s[7]
            GCS_Conf = s[8]
            AH_Output = s[9]
            AH_Acc = s[10]
            AH_Conf = s[11]
            Speaker = s[12]
            study = Study(id, Paragraph_Number, Paragraph_Text, Date_of_Upload,
                          Word_Count, Status, GCS_Output, GCS_Acc, GCS_Conf,
                          AH_Output, AH_Acc, AH_Conf, Speaker)
            db.session.add(study)
            db.session.commit()
            ret["success"] = True
            ret["msg"] = 'Csv file is stored in the psql'
            cnt += 1

    except Exception as exp:
        ret["success"] = False
        ret["error"] = '%s' % exp
    return jsonify(ret)


@app.route('/get_study_material')
def get_study_material():
    ret = {}
    studies = []
    try:
        for data in Study.query.all():
            study = {}
            study['id'] = data.id
            study['Paragraph_Number'] = data.Paragraph_Number
            study['Paragraph_Text'] = data.Paragraph_Text
            study['Date_of_Upload'] = data.Date_of_Upload
            study['Word_Count'] = data.Word_Count
            study['Status'] = data.Status
            study['GCS_Output'] = data.GCS_Output
            study['GCS_Acc'] = data.GCS_Acc
            study['GCS_Conf'] = data.GCS_Conf
            study['AH_Output'] = data.AH_Output
            study['AH_Acc'] = data.AH_Acc
            study['AH_Conf'] = data.AH_Conf
            study['Speaker'] = data.Speaker
            study['created_at'] = data.created_at
            studies.append(study)
        ret['success'] = True
        ret["studies"] = studies
    except Exception as exp:
        ret['success'] = False
        ret['error'] = exp
    return jsonify(ret)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
