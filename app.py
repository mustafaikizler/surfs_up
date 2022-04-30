import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# we will import this after SQLAlchemy dependencies.
from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite")

#Reflect tye database into our classes
Base = automap_base()

#prepare function will use the to reflect the database.

Base.prepare(engine, reflect = True)

# With the database reflected, we can save our references to each table. 
# Again, they'll be the same references as the ones we wrote earlier in this module. 
# We'll create a variable for each of the classes 
# so that we can reference them later, as shown below.

Measurement = Base.classes.measurement
Station = Base.classes.station

#created a session link from Python to our database
session = Session(engine)

#NEXT WE NEED TO DEFINE OUR APP FOR OUR FLASK APP

app = Flask(__name__)

@app.route("/")
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    ''')
@app.route("/api/v1.0/precipitation")
# we will add the function
def precipitation():
    #now we can add the code, one year ago from today
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    #write a query to get the date and precipitation for the previous year.
    precipitation = session.query(Measurement.date, Measurement.prcp).\
         filter(Measurement.date >= prev_year).all()
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
      filter(Measurement.station == 'USC00519281').\
      filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")

def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)
