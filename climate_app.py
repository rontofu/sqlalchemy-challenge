# Import Dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func ,inspect
import datetime as dt

from flask import Flask, jsonify

# Create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect database and tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Establish session link
session = Session(engine)

inspector = inspect(engine)

# Flask
app = Flask(__name__)

# Set Home page

@app.route("/")
def home():
	return (
		f"Available Routes:<br>"
		f"/api/v1.0/precipitation<br>"
		f"/api/v1.0/stations<br>"
		f"/api/v1.0/tobs<br>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    precips = session.query(Measurement).all()
    
    session.close()

    yr_prcip = []
    for precip in precips:
        yr_prcip_dict = {}
        yr_prcip_dict["date"] = precip.date
        yr_prcip_dict["prcp"] = precip.prcp
        yr_prcip.append(yr_prcip_dict)

    return jsonify(yr_prcip)

# Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station).all()
    
    session.close()

    stations_list = []
    for station in stations:
        station_dict = {}
        station_dict["id"] = station.id
        station_dict["station"] = station.station
        station_dict["name"] = station.name
        station_dict["latitude"] = station.latitude
        station_dict["longitude"] = station.longitude
        station_dict["elevation"] = station.elevation
        stations_list.append(station_dict)

    return jsonify(stations_list)

# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.

@app.route("/api/v1.0/tobs")
def temperature():
	last_yr = dt.date(2017, 8, 23) - dt.timedelta(days=365)

	temp_results = session.query(Measurement.tobs).filter(Measurement.date > last_yr).all()
	
	session.close()

	temp_list = list(np.ravel(temp_results))

	return jsonify(temp_list)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>")
def single_date(start):
	
	start_date = dt.datetime.strptime(start,"%Y-%m-%d")
    
	results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.round(func.avg(Measurement.tobs))).\
	filter(Measurement.date >= start_date).all()
	
	session.close() 
	
	result_list = list(np.ravel(results))

	return jsonify(result_list)

# With end date

@app.route("/api/v1.0/<start>/<end>")
def trip_dates(start,end):
	
	start_date = dt.datetime.strptime(start,"%Y-%m-%d")
	end_date = dt.datetime.strptime(end,"%Y-%m-%d")

	results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.round(func.avg(Measurement.tobs))).\
	filter(Measurement.date.between(start_date,end_date)).all()
	
	session.close()    
	
	result_list = list(np.ravel(results))

	return jsonify(result_list)

if __name__ == "__main__":
	app.run(debug=True)