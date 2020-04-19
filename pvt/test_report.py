from numpy import mean
from flask import jsonify
from plotter import response_time_chart
import numpy as np


class report:

	def __init__(self, response_times, test_times, false_clicks = 0):
		self.response_times = np.multiply(response_times, 1000)
		self.test_times = test_times
		self.false_clicks = false_clicks
		self.mean_rt = mean(self.response_times)


	def star_rate(self):
    
	    mean_rt = self.mean_rt
	    false_clicks = self.false_clicks
	    
	    if mean_rt < 300:
	        if false_clicks <= 2:
	            rating = 5
	            comment = ("Your test results indicate that you have extremely quick response times " +
	                      "and none to very few false clicks. "+
	                       "This means that your level of fatigue is very low"
	                      )
	        elif 2 < false_clicks <= 5:
	            rating = 4
	            comment = ("Your test results indicate that you have extremely quick response times " +
	                      "with moderate number of false clicks. " +
	                       "This means that your level fatigue is low."
	                      )
	        else:
	            rating = 3.5
	            comment = ("Your test results indicate that you have extremely quick response times " +
	                      "but fairly high number of false clicks. " +
	                       "This means that you level fatigue is low. " +
	                       "The high number of false clicks may be a sign of hyperactivity."
	                      )
	    
	    elif 300 < mean_rt <= 500:
	        if false_clicks <=2 :
	            rating = 4
	            comment = ("Your test results indicate that you have somewhat quick response times " +
	                       "and none to very few false clicks. "+
	                       "This means that you level of fatigue is mild."
	                      )
	        elif 2 < false_clicks <= 4:
	            rating = 3.5
	            comment = ("Your test results indicate that you have somewhat quick response times " +
	                      "with a few number of false clicks. " +
	                       "This means that your level of fatigue is mild to moderate"
	                      )
	        else:
	            rating = 3
	            comment = ("Your test results indicate that you have somewhat quick response times " +
	                      "with high number of false clicks. " +
	                       "This means that your level of fatigue is moderate"
	                      )
	    
	    elif 500 < mean_rt <= 700:
	        if false_clicks <= 2:
	            rating = 3
	            comment = ("Your test results indicate that you have relatively slow response times " +
	                      "and none to very few false clicks. " +
	                       "This means that your level of fatigue is significant"
	                      )
	        elif 2 < false_clicks <= 5:
	            rating = 2.5
	            comment = ("Your test results indicate that you have relatively slow response times " +
	                      "with a few number of false clicks. " +
	                       "This means that your level of fatigue is significant"
	                      )
	        else:
	            rating = 2
	            comment = ("Your test results indicate that you have relatively slow response times " +
	                      "with high number of false clicks. " +
	                       "This means that your level of fatigue is significantly high"
	                      )
	    
	    elif 700 < mean_rt <= 1000:
	        comment = ("Your test results indicate that you have significantly slow response times. " +
	                       "This means that your level of fatigue is excessive"
	                      )
	        if false_clicks <= 2:
	            rating = 2
	        else:
	            rating = 1.5
	            
	    elif 1000 < mean_rt:
	        comment = ("Your test results indicate that you have extremely slow response times. " +
	                       "This means that your level of fatigue is excessive"
	                      )
	        rating = 1
	        
	              
	    return (jsonify({"rating": rating, "comment": comment}))


	def chart_times(self):
		return response_time_chart(self.response_times, self.test_times)

            
            
            