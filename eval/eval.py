import csv
import glob
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import *


entries = []
birth_year = Column(Integer, nullable=True)
gender = Column(String, nullable=True)
field = Column(String, nullable=True)
experience = Column(Integer, nullable=True)

sigma = Column(Float, nullable=False)
sign = Column(Integer, nullable=False)
slope_type = Column(String, nullable=False)
graph_type = Column(String, nullable=False)

user_slope = Column(Float, nullable=False)
true_slope = Column(Float, nullable=False)

error = Column(Float, nullable=False)
unsigned_error = Column(Float, nullable=False)


for db in glob.glob("*.db"):
    print(db)

    sql_db = "sqlite:///" + db
    engine = create_engine(sql_db, echo=False)
    Session = sessionmaker(bind=engine)
    db_session = Session()
    for q in db_session.query(DataEntry,User).join(DataEntry.user).all():
        entries.append([
           q[1].birth_year,
            q[1].gender,
            q[1].field,
            q[1].experience,
            q[0].sigma,
            q[0].sign,
            q[0].slope_type,
            q[0].graph_type,
            np.round(q[0].user_slope, 4),
            np.round(q[0].true_slope, 4),
            np.round(q[0].error, 4),
            np.round(q[0].unsigned_error, 4)
        ])

with open("out.csv", "w", newline="") as f:
    writer = csv.writer(f, delimiter = ";")
    writer.writerow(["birth_year", "gender", "field", "experience", "sigma",
                     "sign", "slope_type", "graph_type", "user_slope", "true_slope", "error", "unsigned_error"])
    for q in entries:
        writer.writerow(q)
