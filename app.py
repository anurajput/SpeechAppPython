import os
import jwt
import traceback
import datetime
from OpenSSL import SSL
from flask_cors import CORS
from google_api import run_google_api
from functools import wraps
from difflib import SequenceMatcher
from werkzeug.utils import secure_filename
from flask import Flask, request, redirect, render_template, jsonify
from flask.ext.bcrypt import Bcrypt
from models import app, db, User, Study, Recording

bcrypt = Bcrypt(app)

cors = CORS(app, resources={r'/api/*': {'origins': '*'}})
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


@app.route('/api/index')
def index():
    temp_data = {'title': 'SpeechApp'}
    return render_template('index.html', **temp_data)


@app.route('/api/voice')
def voice():
    temp_data = {'title': 'SpeechVoice'}
    return render_template('voice.html', **temp_data)


@app.route('/api/speech')
def speech():
    temp_data = {'title': 'SpeechVoice'}
    return render_template('speech-to-text.html', **temp_data)


@app.route('/api/demo')
def demo():
    return render_template('demo.html')


@app.route('/api/get_demo', methods=['POST'])
def get_demo():
    try:
        print '======================', request.form
    except:
        pass
    return "hoo"


@app.route('/api/user_registration', methods=['POST'])
def user_registration():
    ret = {}
    try:
        id = request.form['id']
        name = request.form['name']
        email = request.form['email']
        pswd = request.form['password']
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


@app.route('/api/user_login', methods=['POST'])
def user_login():
    ret = {}
    try:
        email = request.form['email']
        pswd = request.form['password']
        query = User.query.filter_by(email=email).first()

        # check email is valid or not
        if not query:
            ret['msg'] = 'Login failed! Email and Password not match'
            ret['success'] = False
            return jsonify(ret)
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
            return jsonify(ret)
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
file_path = '%s/%s' % (dir_path, 'uploads')
UPLOAD_FOLDER = file_path
ALLOWED_EXTENSION = set(['wav', 'mp3', 'txt', 'csv', 'png', 'jpg', 'gif', 'pdf'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() \
                               in ALLOWED_EXTENSION


@app.route('/api/add_study', methods=['POST'])
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

    return 'file uploads successfully'


@app.route('/api/study')
@token_required
def study():

    ret = {}
    try:
        # count the no of lines
        with open('uploads/study.csv') as f:
            for i, l in enumerate(f):
                pass
        total_lines = i + 1

        # getting the data from the csv file
        csv_file = open('uploads/study.csv', 'r')

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
                          Paragraph_Type, Word_Count, Status, GCS_Output, GCS_Acc,
                          GCS_Conf, AH_Output, AH_Acc, AH_Conf, Speaker)
            db.session.add(study)
            db.session.commit()
            ret['success'] = True
            ret['msg'] = 'Csv file is stored in the psql'
            cnt += 1

    except Exception as exp:
        ret['success'] = False
        ret['error'] = '%s' % exp
    return jsonify(ret)


@app.route('/api/get_study_material')
@token_required
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
            study['Paragraph_Type'] = data.Paragraph_Type
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
        ret['studies'] = studies
    except Exception as exp:
        ret['success'] = False
        ret['error'] = exp
    return jsonify(ret)


@app.route('/api/add_recording', methods=['POST'])
def add_recording():
    ret = {}
    prefix = request.base_url[:-len('/api/add_recording')]
    try:
        id = request.form['id']
        user_id = request.form['user_id']
        study_id = request.form['study_id']

        # recording uploads
        filename = ''
        recording_file = request.files['recording_file']

        if recording_file.filename == '':
            flash('Nop Selectd file')
            return redirect(request.url)
        if recording_file and allowed_file(recording_file.filename):
            filename = secure_filename(recording_file.filename)
            recording_file.save(os.path.join(app.config
                                             ['UPLOAD_FOLDER'], filename))
            recording = '%s/%s' % (file_path, filename)

        save_recording_file_url = '%s/uploads/%s' % (prefix, filename)

        # save in database
        recording = Recording(id, user_id, study_id, save_recording_file_url)
        db.session.add(recording)
        db.session.commit()
        ret['success'] = True
        ret['msg'] = 'recording added successfully'
    except Exception as exp:
        print 'add_recording() :: Got excepion: %s' % exp
        print(traceback.format_exc())
        ret['msg'] = '%s' % exp
        ret['success'] = False
    return jsonify(ret)


@app.route('/api/get_recording')
def get_recording():
    ret = {}
    recordings = []
    try:
        recording = {}
        for data in Recording.query.all():
            recording['id'] = data.id
            recording['user_id'] = data.user_id
            recording['study_id'] = data.study_id
            recording['recording_file'] = data.recording_file
            recordings.append(recording)
        ret['success'] = True
        ret['recordings'] = recordings
    except Exception as exp:
        print 'get_recording() :: Got exception: %s' % exp
        print(traceback.format_exc())
        ret['success'] = False
        ret['error'] = '%s' % exp
    return jsonify(ret)


@app.route('/api/comparison')
def comparison():
    ret = {}
    audio = Recording.query.all()
    print '', audio
    google_data = run_google_api()
    # print "-------+++++++: [%s]" % google_data
    file1 = open('uploads/study.csv', 'r')
    data = file1.read()
    file2 = open('uploads/study_file.csv', 'r')
    data2 = file2.read()
    comparison = str(SequenceMatcher(None, data, data2).ratio() * 100)
    ret['Comparison_percentage'] = comparison
    ret['success'] = True
    return jsonify(ret)


@app.route('/api/matching_test', methods=['POST'])
def matching_test():
    ret = {}
    prefix = request.base_url[:-len('/api/matching_test')]

    recording_path = None

    try:
        text = request.form['text']
        # recording uploads
        filename = ''
        rec_file = request.files['rec_file']

        if rec_file.filename == '':
            flash('Nop Selectd file')
            return redirect(request.url)
        if rec_file and allowed_file(rec_file.filename):
            filename = secure_filename(rec_file.filename)
            rec_file.save(os.path.join(app.config
                                             ['UPLOAD_FOLDER'], filename))
            recording_path = '%s/%s' % (file_path, filename)

        save_recording_file_url = '%s/uploads/%s' % (prefix, filename)
        rec_text = run_google_api(recording_path)
        comparison = str(SequenceMatcher(None, text, rec_text).ratio() * 100)
        ret['Comparison_percentage'] = comparison
        ret['success'] = True
    except Exception as exp:
        print 'matching_test() :: Got Exception: %s' % exp
        print(traceback.format_exc())
        ret['msg'] = '%s' % exp
        ret['success'] = False
    return jsonify(ret)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    context = ('server.crt', 'server.key')
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)

