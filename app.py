from flask import Flask, request, send_file, jsonify, render_template
from db import api
import mysql.connector
import os
from pvt.test_report import report
from flask_googlemaps import GoogleMaps, Map


app = Flask(__name__, template_folder="maps_template")
app.config["DEBUG"] = True
app.config['GOOGLEMAPS_KEY'] = os.environ["gcp_key"]
GoogleMaps(app)



@app.route('/crashes_tod_atm', methods=[ 'POST'])
def crashes_tod_atm():
	content = request.json

	try:
		# extract user gps coordinates
		lat = float(content["lat"])
		lon	= float(content["lon"])
		# kms = float(content["kms"])

		# create plot 
		tod_atm = api( lat, lon).crash_tod_atm()
		return send_file(tod_atm, attachment_filename='plot.png', mimetype='image/png')
	
	except KeyError:
		# if lat or lon data is not received in client request
		return jsonify({"res": "invalid/missing data"})


	
 


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


@app.route('/map', methods = ["GET", "POST"])
def mapview():
    # creating a map in the view
    mymap = Map(
        identifier="view-side",
        lat=37.4419,
        lng=-122.1419,
        markers=[(37.4419, -122.1419)]
    )
    sndmap = Map(
        identifier="sndmap",
        lat=37.4419,
        lng=-122.1419,
        markers=[
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
             'lat': 37.4419,
             'lng': -122.1419,
             'infobox': "<b>Hello World</b>"
          },
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
             'lat': 37.4300,
             'lng': -122.1400,
             'infobox': "<b>Hello World from other place</b>"
          }
        ]
    )
    return render_template('example.html', mymap=mymap, sndmap=sndmap)
    



if __name__ == "__main__":
	app.run(debug=True, host = "0.0.0.0")
