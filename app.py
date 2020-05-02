from flask import Flask, request, send_file, jsonify
from db import api
import mysql.connector
import os
from pvt.test_report import report
from maps import gmap


app = Flask(__name__)
app.config["DEBUG"] = True




@app.route('/crashes_tod_atm', methods=[ 'POST'])
def crashes_tod_atm():
	content = request.json

	try:
		# extract user gps coordinates
		lat = float(content["lat"])
		lon	= float(content["lon"])

		# create plot 
		tod_atm = api( lat, lon).crash_tod_atm()
		return send_file(tod_atm, attachment_filename='plot.png', mimetype='image/png')
	
	except KeyError:
		# if lat or lon data is not received in client request
		return jsonify({"res": "invalid/missing data"})


	
 


@app.route('/local_crashes_person', methods=[ "POST"])
def local_crashes_person():
	content = request.json

	# extract lat and lon

	lat = float(content["lat"])
	lon = float(content["lon"])

	# create api object
	person_crashes = api(lat, lon).crash_by_person()

	# return relevant method output
	return send_file(person_crashes, attachment_filename='plot.png', mimetype='image/png')



@app.route("/pvt_data/<type>", methods = ["POST"])
def pvt_data(type):
	content = request.json
	reaction_times = content["reaction_times"]
	test_times = content["test_times"]
	false_clicks = content["false_clicks"]

	if(len(reaction_times) == len(test_times) > 0):

		# save to db (temp ops)

		api().save_pvt(reaction_times, test_times, false_clicks)

		# create a report class object
		reporter = report(reaction_times, test_times, false_clicks)

		# execute the requested method
		if type == "summary":
			return reporter.star_rate()
		elif type == "chart":
			plot = reporter.chart_times()
			return send_file(plot, attachment_filename='plot.png', mimetype='image/png')

	elif (len(reaction_times) == len(test_times) == 0):
		return(jsonify({"rating": None, "comment": "insufficient data. please re-take the test", "level": None}))
	else:
		return(jsonify({"res": "invalid data"}))




@app.route('/map', methods = [ "POST"])
def map():
	content = request.json

	origin = gmap.Place()
	dest = gmap.Place()

	origin.search(content["origin"]["query"], content["origin"]["qry_type"])
	dest.search(content["dest"]["query"], content["dest"]["qry_type"])

	my_route = gmap.Directions(origin, dest)
	my_route.get_route()
	return(my_route.plot_folium())
    
   
    



if __name__ == "__main__":
	app.run(debug=True, host = "0.0.0.0")
