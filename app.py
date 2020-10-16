import numpy as np
import os

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################


@app.route("/")
def welcome():
    """Home Page"""
    """List all routes that are available"""
    return (
        f"==== Available Routes ====<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tob<br/>"
        f"/api/v1.0/yyyy-mm-dd<br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    """Convert the query results to a dictionary using date as the key and 
    prcp as the value."""
    session = Session(engine)
    result = session.query(measurement.date, measurement.prcp).all()
    session.close()

    precipitation = []
    for date, prcp in result:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

@app.route('/api/v1.0/stations')
def stations():
    """Return a JSON list of stations from the dataset."""
    session = Session(engine)
    result = session.query(station.station, station.name, station.latitude, station.longitude, station.elevation).all()
    session.close()

    stations = []
    for st, name, lat, lng, elv in result:
        station_dict = {}
        station_dict["Station"] = st
        station_dict["Name"] = name
        station_dict["Latitude"] = lat
        station_dict["Longitude"] = lng
        station_dict["Elevation"] = elv
        stations.append(station_dict)

    return jsonify(stations)

@app.route('/api/v1.0/tob')
def tob():
    """Query the dates and temperature observations of the most active station
     for the last year of data."""
    session = Session(engine)
    last_data_date = (session.query(measurement).order_by(measurement.date.desc()).first()).date
    # print(f"Date of Last Data Point: {last_data_date}")
    last_date_split = last_data_date.split("-")
    last_yr = int(last_date_split[0])
    query_yr = last_yr - 1
    query_date = str(query_yr) + last_data_date[4:]
    sel = [measurement.date, measurement.tobs]
    result = session.query(*sel).filter(measurement.date >= query_date).all()
    session.close()

    tobs = []
    for date, tob in result:
        tob_dict = {}
        tob_dict["Date"] = date
        tob_dict["tobs"] = tob
        tobs.append(tob_dict)

    return jsonify(tobs)

@app.route('/api/v1.0/<start>')
def start_given(start):
    """When given the start only, calculate TMIN, TAVG, and TMAX for all 
    dates greater than and equal to the start date."""
    session = Session(engine)
    result = session.query(func.min(measurement.tobs), 
        func.avg(measurement.tobs), 
        func.max(measurement.tobs)).filter(measurement.date >= start).all()

    tobs = []
    for mini, avg, maxi in result:
        tob_dict = {}
        tob_dict["Minimum"] = mini
        tob_dict["Average"] = avg
        tob_dict["Maximum"] = maxi
        tobs.append(tob_dict)

    return jsonify(tobs)  

@app.route('/api/v1.0/<start>/<end>')
def both_given(start, end):
    """When given the start and the end date, calculate the TMIN, TAVG, and TMAX 
    for dates between the start and end date inclusive."""
    session = Session(engine)
    result = session.query(func.min(measurement.tobs), 
        func.avg(measurement.tobs), 
        func.max(measurement.tobs)).filter(and_(measurement.date >= start,
             measurement.date <= end)).all()

    tobs = []
    for mini, avg, maxi in result:
        tob_dict = {}
        tob_dict["Minimum"] = mini
        tob_dict["Average"] = avg
        tob_dict["Maximum"] = maxi
        tobs.append(tob_dict)

    return jsonify(tobs)


if __name__ == '__main__':
    app.run(debug=True)
