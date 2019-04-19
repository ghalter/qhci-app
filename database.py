"""

"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String, Integer, Float, Column, ForeignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker
from flask_sqlalchemy import SQLAlchemy

import csv

Base = declarative_base()
db = SQLAlchemy()

import json

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    entries = relationship("DataEntry", back_populates="user")

class DataEntry(Base):
    """
    """
    __tablename__ = 'data_entries'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
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


def import_trial_tables(path_inner, path_outer):
    import os
    p = os.path.abspath("database.db")
    engine = create_engine("sqlite:///" + p, echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autocommit=False)
    db_session = Session()


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



if __name__ == '__main__':
    import_trial_tables("resources/Experiment 3_ Inner - 190419 125015.csv",
                        "resources/Experiment 3_ Outer - 190419 125010.csv")
