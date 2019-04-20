"""

"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String, Integer, Float, Column,MetaData, ForeignKey, create_engine
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import relationship, sessionmaker
from flask_sqlalchemy import SQLAlchemy

import csv

Base = declarative_base()
db = SQLAlchemy()

import json

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    birth_year = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    field = Column(String, nullable=True)
    experience = Column(Integer, nullable=True)

    entries = relationship("DataEntry", back_populates="user")

class DataEntry(Base):
    """
    """
    __tablename__ = 'data_entries'
    id = Column(Integer, primary_key=True)
    sigma = Column(Float, nullable=False)
    sign = Column(Integer, nullable=False)
    slope_type = Column(String, nullable=False)
    graph_type = Column(String, nullable=False)

    user_slope = Column(Float, nullable=False)
    true_slope = Column(Float, nullable=False)

    error = Column(Float, nullable=False)
    unsigned_error = Column(Float, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="entries")



class TrialTableOuter(Base):
    __tablename__ = 'trial_table_outer'

    id = Column(Integer, primary_key=True)
    participant_id = Column(String, nullable=False)
    trial_id =Column(Integer, nullable=False)
    slope_type = Column(String, nullable=False)

class TrialTableInner(Base):
    __tablename__ = 'trial_table_inner'

    id = Column(Integer, primary_key=True)
    participant_id = Column(String, nullable=False)
    trial_id = Column(Integer, nullable=False)
    block_1 = Column(Integer, nullable=False)
    block_2 = Column(Integer, nullable=False)
    block_3 = Column(Integer, nullable=False)
    plot_type = Column(String, nullable=False)
    residual = Column(String, nullable=False)
    slope = Column(String, nullable=False)


class AlchemyEncoder(json.JSONEncoder):
    """
    A JSONEncoder resursively parsing all objects to JSON.

    """
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data)  # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields
        print("Encoded")
        return json.JSONEncoder.default(self, obj)


def import_trial_tables(path_inner, path_outer):
    import os
    p = os.path.abspath("database.db")
    engine = create_engine("sqlite:///" + p, echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autocommit=False)
    db_session = Session()

    if len(db_session.query(TrialTableInner).all()) > 0:
        print("Database already imported")
        return
    else:
        print("Importing Touchstone tables")

    with open(path_outer, "r") as f:
        reader = csv.reader(f)
        for i, r in enumerate(reader):
            if i == 0:
                idx_participant = r.index("ParticipantID")
                idx_trial = r.index("TrialID")
                idx_slope_type = r.index("ID")
            else:
                q = TrialTableOuter(participant_id = r[idx_participant], trial_id = r[idx_trial], slope_type=r[idx_slope_type].lower())
                db_session.add(q)
    with open(path_inner, "r") as f:
        reader = csv.reader(f)
        for i, r in enumerate(reader):
            print(r)
            if i == 0:
                idx_participant = r.index("ParticipantID")
                idx_trial = r.index("TrialID")
                idx_block1 = r.index("Block1")
                idx_block2 = r.index("Block2")
                idx_block3 = r.index("Block3")
                idx_chart_type = r.index("C")
                idx_residuals = r.index("R")
                idx_slope = r.index("S")
            else:
                chart_type = r[idx_chart_type].lower()
                residuals = float(r[idx_residuals].replace("R_", "").replace("_", "."))
                slope = float(r[idx_slope].replace("S_", "").replace("_", "."))
                q = TrialTableInner(participant_id = r[idx_participant],
                                trial_id = r[idx_trial],
                                block_1 = r[idx_block1],
                                block_2 = r[idx_block2],
                                block_3 = r[idx_block3],
                                plot_type = chart_type,
                                residual = residuals,
                                slope=slope)
                db_session.add(q)

    db_session.commit()

import zipfile
import datetime
import platform

def export_all_tables():
    newline = "\n"
    if platform.system() == "Windows":
        newline = ""
    with open("trial.csv", "w", newline=newline) as f:
        outcsv = csv.writer(f)
        records = db.session.query(DataEntry).all()
        outcsv.writerow([column.name for column in DataEntry.__mapper__.columns])
        [outcsv.writerow([getattr(curr, column.name) for column in DataEntry.__mapper__.columns]) for curr in records]
    with open("participants.csv", "w", newline=newline) as f:
        outcsv = csv.writer(f)
        records = db.session.query(User).all()
        outcsv.writerow([column.name for column in User.__mapper__.columns])
        [outcsv.writerow([getattr(curr, column.name) for column in User.__mapper__.columns]) for curr in records]

    list_files = ["trial.csv", "participants.csv"]
    zip_name = "export_" + datetime.datetime.now().strftime(format='%H-%M_%d-%m-%Y') + ".zip"
    with zipfile.ZipFile(zip_name, 'w') as zipMe:
        for file in list_files:
            zipMe.write(file, compress_type=zipfile.ZIP_DEFLATED)

    return zip_name


if __name__ == '__main__':
    import_trial_tables("resources/Experiment 3_ Inner - 190419 125015.csv",
                        "resources/Experiment 3_ Outer - 190419 125010.csv")
