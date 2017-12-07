#
# script for various ORM models for project
#

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import ForeignKey

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql://speechapp:123@localhost/speechdb'
db = SQLAlchemy(app)


class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(90))
    email = db.Column(db.String(90), unique=True)
    password = db.Column(db.String(90))
    created_at = db.Column(db.TIMESTAMP,
                           default=datetime.utcnow, nullable=False)

    def __init__(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password

    @property
    def serialize(self):

        """ Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'email': self.email,
            'password': self.password,
            'created_at': self.created_at
        }


class Study(db.Model):

    __tablename__ = 'study'

    id = db.Column(db.BigInteger, primary_key=True)
    # user_id = db.Column(db.BigInteger, ForeignKey('user.id'))
    Paragraph_Number = db.Column(db.BigInteger)
    Paragraph_Text = db.Column(db.String(1024))
    Date_of_Upload = db.Column(db.String(200))
    Paragraph_Type = db.Column(db.String(200))
    Word_Count = db.Column(db.BigInteger)
    Status = db.Column(db.String(90))
    GCS_Output = db.Column(db.String(1024))
    GCS_Acc = db.Column(db.String(200))
    GCS_Conf = db.Column(db.String(200))
    AH_Output = db.Column(db.String(1024))
    AH_Acc = db.Column(db.String(1024))
    AH_Conf = db.Column(db.String(200))
    Speaker = db.Column(db.String(200))
    created_at = db.Column(db.TIMESTAMP,
                           default=datetime.utcnow, nullable=False)

    def __init__(self, id, Paragraph_Number, Paragraph_Text, Date_of_Upload,
                 Paragraph_Type, Word_Count, Status, GCS_Output, GCS_Acc,
                 GCS_Conf, AH_Output, AH_Acc, AH_Conf, Speaker):
        self.id = id
        self.Paragraph_Number = Paragraph_Number
        self.Paragraph_Text = Paragraph_Text
        self.Date_of_Upload = Date_of_Upload
        self.Paragraph_Type = Paragraph_Type
        self.Word_Count = Word_Count
        self.Status = Status
        self.GCS_Output = GCS_Output
        self.GCS_Acc = GCS_Acc
        self.GCS_Conf = GCS_Conf
        self.AH_Output = AH_Output
        self.AH_Acc = AH_Acc
        self.AH_Conf = AH_Conf
        self.Speaker = Speaker

    @property
    def serialize(self):

        """Return object data in easily serialzeable format"""
        return {
            'id': self.id,
            'Paragraph_Number': self.Paragraph_Number,
            'Paragraph_Text': self.Paragraph_Text,
            'Date_of_Upload': self.Date_of_Upload,
            'Paragraph_Type': self.Paragraph_Type,
            'Word_Count': self.Word_Count,
            'Status': self.Status,
            'GCS_Output': self.GCS_Output,
            'GCS_Acc': self.GCS_Acc,
            'GCS_Conf': self.GCS_Conf,
            'AH_Output': self.AH_Output,
            'AH_Acc': self.AH_Acc,
            'AH_Conf': self.AH_Conf,
            'Speaker': self.Speaker,
            'created_at': self.created_at
        }


class Recording(db.Model):

    __tablename__ = 'recording'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, ForeignKey('user.id'))
    study_id = db.Column(db.BigInteger, ForeignKey('study.id'))
    recording_file = db.Column(db.String(90))
    created_at = db.Column(db.TIMESTAMP,
                           default=datetime.utcnow, nullable=False)

    def __init__(self, id, user_id, study_id, recording_file):
        self.id = id
        self.user_id = user_id
        self.study_id = study_id
        self.recording_file = recording_file

    @property
    def serialize(self):

        """Return object data in easily serialzeable format"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'study_id': self.study_id,
            'recording_file': self.recording_file
        }


if __name__ == '__main__':
    try:
        db.create_all()
        print "===================== [db created] ====================="
    except Exception as exp:
        print "[Postgres Models] :: main() :: Got Exception: %s" % exp
        print "===================== [db not created] ================="
