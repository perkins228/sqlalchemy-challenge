import numpy as np
import datetime as dt
import pandas as pd
from pandas.core.tools.datetimes import Scalar
import re

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_
from sqlalchemy.sql import exists  

from flask import Flask, json, jsonify


engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Station = Base.classes.station
Measurement = Base.classes.measurement


app = Flask(__name__)
#homepage
@app.route("/")
def home():
     return (
         f"Welcome to the Climate App <br/>"
         f"Available Routes:<br/>"
         f"/api/v1.0/precipitation<br/>"
         f"/api/v1.0/stations<br/>"
         f"/api/v1.0/tobs<br/>"
         f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
         f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"
         
         )

@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)

    results = session.query(Measurement.date, Measurement.prcp).\
        order_by(Measurement.date).all()

    prcp_list =[]
    for result in results:
        prcp_dict = {}
        prcp_dict["date"] = result.date 
        prcp_dict["precipitation"] = result.prcp
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)

    stations = session.query(Station.name).all()
    all_stations = [item for station in stations for item in station]


    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    year_ago = dt.date(2017, 8, 18) - dt.timedelta(days = 365)
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter((Measurement.station == "USC00519281"), (Measurement.date >= year_ago)).\
            order_by(Measurement.date.desc()).all()
    
    # tobs_dict = {data[0]: data[1] for data in tobs_data}
    tobs_list = []
    for data in tobs_data:
        tobs_dict ={}
        tobs_dict["Date"] = data.date
        tobs_dict["Temperature"] = data.tobs
        tobs_list.append(tobs_dict)
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    min_date = session.query(func.min(Measurement.date))
    min_date_str = min_date.scalar()
    max_date = session.query(func.max(Measurement.date))
    max_date_str = max_date.scalar()
    min_max_average = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start)
    
    date_exists = session.query(exists().where(Measurement.date == start)).scalar()

    if date_exists:
        temps_list =[]
        for temps in min_max_average:
            temps_dict = {}
            temps_dict["Min Temp"] = temps[0]
            temps_dict["Average Temp"] = temps[1]
            temps_dict["Max Temp"] = temps[2]
            temps_list.append(temps_dict)

        return jsonify(temps_list)

    return jsonify({"Error": f"Input Date {start} not valid. Date Range is {min_date_str} to {max_date_str}"}), 404

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)
    min_date = session.query(func.min(Measurement.date))
    min_date_str = min_date.scalar()
    max_date = session.query(func.max(Measurement.date))
    max_date_str = max_date.scalar()


    min_max_avg = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()

    start_exists = session.query(exists().where(Measurement.date == start)).scalar()
    end_exists = session.query(exists().where(Measurement.date == end)).scalar()

    if start_exists and end_exists:
        temp_list =[]
        for temps in min_max_avg:
            temps_dict = {}
            temps_dict["Min Temp"] = temps[0]
            temps_dict["Average Temp"] = temps[1]
            temps_dict["Max Temp"] = temps[2]
            temp_list.append(temps_dict)

        return jsonify(temp_list)

    return jsonify({"Error": f"Input Date(s) not valid. Date Range is {min_date_str} to {max_date_str}"}), 404

if __name__ == "__main__":
    app.run(debug=True)
