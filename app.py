import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify,render_template
import pandas as pd
import datetime as dt

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)


@app.route("/")
def home():
    return (
        f"For Past Weather Data in Hawaii:<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt; <br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)

    results = session.query(Measurement.date,Measurement.prcp).all()
    prcp_li = []
    for da,pr in results:
        pr_dict = {da:pr}
        prcp_li.append(pr_dict)

    
    return jsonify(prcp_li)

@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)
    results = session.query(Station.station).all()

    stations = []

    for st in results:
        stations.append(st[0])

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    dates = session.query(Measurement.date).\
        filter(Measurement.date > year_ago).all()

    tob = session.query(Measurement.tobs).\
        filter(Measurement.date > year_ago).all()

    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > year_ago).all()

    tobs_list = []
    for date, tobs in results:
        tobs_dict = {date:tobs}
        tobs_list.append(tobs_dict)


    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def summary(start):

    session = Session(engine)

    results = session.query(Measurement.date, Measurement.tobs).all()
    summ_list = []
    list_2 = []

    for date,temp in results:
        summ_dict = {}
        summ_dict["Date"] = date
        summ_dict["Temp"] = temp
        dict_2 = {date:temp}
        list_2.append(dict_2)
        summ_list.append(summ_dict)
    # This just gives info for the date entered.
    tobs_start = []
    for dic in list_2:
        for key in dic:
            if key >= start:
                for val in dic.values():
                    tobs_start.append(val)

    # return jsonify(f"For the date {start}: Max Temp: {max(tobs_start)}, Min Temp: {min(tobs_start)}, Mean Temp: {sum(tobs_start)/len(tobs_start)} ")

    key_list = []
    temp_list = []
    for dic in list_2:
        for key in dic:
            if key >= start:
                key_list.append(key)
                for val in dic.values():
                    temp_list.append(val)

    df = pd.DataFrame({"Date":key_list,"Temp":temp_list})
    group = df.groupby(["Date"])
    max_temp = group["Temp"].max()
    min_temp = group["Temp"].min()
    mean_temp = group["Temp"].mean()
    dates = group["Date"]
    df_2 = pd.DataFrame({"Date":dates, "Max Temp":max_temp})
    max_list = max_temp.tolist()
    min_list = min_temp.tolist()
    mean_list = mean_temp.tolist()
    return (
        f"The max temps for the dates {start} to 2017-08-23: {max_list} <br/> <br/>"
        f"The min temps for the dates {start} to 2017-08-23: {min_list} <br/> <br/>"
        f"The mean temps for the dates {start} to 2017-08-23: {mean_list}"
        )


@app.route("/api/v1.0/<start>/<end>")
def tobs_start_end(start, end):

    session = Session(engine)

    results = session.query(Measurement.date, Measurement.tobs).all()
    summ_list = []
    list_2 = []

    for date,temp in results:
        summ_dict = {}
        summ_dict["Date"] = date
        summ_dict["Temp"] = temp
        dict_2 = {date:temp}
        list_2.append(dict_2)
        summ_list.append(summ_dict)

    tobs_vals = {}
    tobs_vals_list = []
    key_list = []
    temp_list = []
    for dic in list_2:
        for key in dic:
            if key >= start and key <= end:
                key_list.append(key)
                tobs_vals["date"] = key
                tobs_vals_list.append(tobs_vals)
                for val in dic.values():
                    temp_list.append(val)
                    tobs_vals["temp"] = val
                    tobs_vals_list.append(tobs_vals)

    df = pd.DataFrame({"Date":key_list,"Temp":temp_list})
    group = df.groupby(["Date"])
    max_temp = group["Temp"].max()
    min_temp = group["Temp"].min()
    mean_temp = group["Temp"].mean()
    dates = group["Date"]
    df_2 = pd.DataFrame({"Date":dates, "Max Temp":max_temp})
    max_list = max_temp.tolist()
    min_list = min_temp.tolist()
    mean_list = mean_temp.tolist()
    return (
        f"The max temps for the dates {start} to {end}: {max_list} <br/> <br/>"
        f"The min temps for the dates {start} to {end}: {min_list} <br/> <br/>"
        f"The mean temps for the dates {start} to {end}: {mean_list}"
        )


if __name__ == "__main__":
    app.run(debug=True)