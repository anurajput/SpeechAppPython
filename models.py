#
# script for various ORM models for project
#

from flask import Flask
# from app import app
import os
# from eve import Eve
# from eve_sqlalchemy import SQL
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import ForeignKey

app = Flask(__name__)
# tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
#                          'templates')
# app = Eve('SpeechApp', template_folder=tmpl_dir)

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql://speechapp:123@localhost/speechdb'
db = SQLAlchemy(app)


class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(90))
    email = db.Column(db.String(90))
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


class Paragraph(db.Model):

    __tablename__ = 'paragraph'

    id = db.Column(db.BigInteger, primary_key=True)
    paragraph = db.Column(db.String(90))
    user_id = db.Column(db.BigInteger, ForeignKey('user.id'))
    created_at = db.Column(db.TIMESTAMP,
                           default=datetime.utcnow, nullable=False)

    def __init__(self, id, paragraph, user_id, created_at):
        self.id = id
        self.paragraph = paragraph
        self.user_id = user_id
        self.created_at = created_at

    @property
    def serialize(self):
        
        return {
            'id': self.id,
            'paragraph': self.paragraph,
            'user_id': self.user_id,
            'created_at': self.created_at
        }


class Study(db.Model):

    __tablename__ = 'study'

    id = db.Column(db.BigInteger, primary_key=True)
    # user_id = db.Column(db.BigInteger, ForeignKey('user.id'))
    Paragraph_Number = db.Column(db.BigInteger)
    Paragraph_Text = db.Column(db.String(90))
    Date_of_Upload = db.Column(db.String(90))
    Word_Count = db.Column(db.BigInteger)
    Status = db.Column(db.String(90))
    GCS_Output = db.Column(db.String(90))
    GCS_Acc = db.Column(db.String(90))
    GCS_Conf = db.Column(db.String(90))
    AH_Output = db.Column(db.String(90))
    AH_Acc = db.Column(db.String(90))
    AH_Conf = db.Column(db.String(90))
    Speaker = db.Column(db.String(90))
    created_at = db.Column(db.TIMESTAMP,
                           default=datetime.utcnow, nullable=False)

    def __init__(self, id, Paragraph_Number, Paragraph_Text, Date_of_Upload,
                 Word_Count, Status, GCS_Output, GCS_Acc, GCS_Conf, AH_Output,
                 AH_Acc, AH_Conf, Speaker):
        self.id = id
        self.Paragraph_Number = Paragraph_Number
        self.Paragraph_Text = Paragraph_Text
        self.Date_of_Upload = Date_of_Upload
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


if __name__ == '__main__':
    try:
        db.create_all()
        print "===================== [db created] ====================="
    except Exception as exp:
        print "[Postgres Models] :: main() :: Got Exception: %s" % exp
        print "===================== [db not created] ================="
