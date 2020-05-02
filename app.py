from flask import Flask, request, send_file, jsonify
import os
from pvt.test_report import report
from maps.handler import map_handler


app = Flask(__name__)
app.config["DEBUG"] = True




@app.route("/pvt_data/<type>", methods = ["POST"])
def pvt_data(type):
	content = request.json
	reaction_times = content["reaction_times"]
	test_times = content["test_times"]
	false_clicks = content["false_clicks"]

	if(len(reaction_times) == len(test_times) > 0):

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


	return(map_handler(content))
    
   
    



if __name__ == "__main__":
	app.run(debug=True, host = "0.0.0.0")
