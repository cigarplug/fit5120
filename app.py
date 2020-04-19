from flask import Flask, request, send_file, jsonify
from db import api
import mysql.connector
import os
from pvt.test_report import report


app = Flask(__name__)
app.config["DEBUG"] = True



@app.route('/crashes_tod_atm', methods=[ 'POST'])
def crashes_tod_atm():
	content = request.json
	lat = float(content["lat"])
	lon = float(content["lon"])
	# kms = float(content["kms"])

	tod_atm = api( lat, lon).crash_tod_atm()
	return send_file(tod_atm, attachment_filename='plot.png', mimetype='image/png')
 


@app.route('/local_crashes_person', methods=[ 'GET', "POST"])
def local_crashes_person():
	content = request.json

	# extract lat and lon

	lat = float(content["lat"])
	lon = float(content["lon"])

	# create api object
	person_crashes = api(lat, lon).crash_by_person()

	# return relevant method output
	return send_file(person_crashes, attachment_filename='plot.png', mimetype='image/png')



@app.route("/pvt_data", methods = ["POST"])
def pvt_data():
	content = request.json
	reaction_times = content["reaction_times"]
	test_times = content["test_times"]
	false_clicks = content["false_clicks"]

	if(len(reaction_times) == len(test_times)):
		reporter = report(reaction_times, test_times, false_clicks)
		return reporter.star_rate()

	else:
		return(jsonify({"res": "invalid data"}))



if __name__ == "__main__":
	app.run(debug=True, host = "0.0.0.0")
