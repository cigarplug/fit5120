from numpy import mean
from flask import jsonify
from plotter import response_time_chart
import numpy as np


class report:

	def __init__(self, response_times, test_times, false_clicks = 0):
		self.response_times = response_times
		self.test_times = test_times
		self.false_clicks = false_clicks
		


	def star_rate(self):
    
	    mean_rt = np.mean(np.multiply(self.response_times, 1000))
	    false_clicks = self.false_clicks
	    
	    if mean_rt < 300:
	        if false_clicks <= 2:
	            rating = 5
	            comment = ("Your test results indicate that you have extremely quick response times " +
	                      "and none to very few false clicks."
	                      )
	            fatigue_level = "Very low"
	        elif 2 < false_clicks <= 5:
	            rating = 4
	            comment = ("Your test results indicate that you have extremely quick response times " +
	                      "with moderate number of false clicks. "
	                      )
	            fatigue_level = "Low"
	        else:
	            rating = 3.5
	            comment = ("Your test results indicate that you have extremely quick response times " +
	                      "but fairly high number of false clicks. " +
	                       "The high number of false clicks may be a sign of hyperactivity."
	                      )
	            fatigue_level = "Low"
	    
	    elif 300 < mean_rt <= 500:
	        if false_clicks <=2 :
	            rating = 4
	            comment = ("Your test results indicate that you have somewhat quick response times " +
	                       "and none to very few false clicks."
	                      )
	            fatigue_level = "Relatively Low"
	        elif 2 < false_clicks <= 4:
	            rating = 3.5
	            comment = ("Your test results indicate that you have somewhat quick response times " +
	                      "with a few number of false clicks."
	                      )
	            fatigue_level = "Mild to moderate"
	        else:
	            rating = 3
	            comment = ("Your test results indicate that you have somewhat quick response times " +
	                      "with high number of false clicks."
	                      )
	            fatigue_level = "Moderate"
	    
	    elif 500 < mean_rt <= 700:
	        if false_clicks <= 2:
	            rating = 3
	            comment = ("Your test results indicate that you have relatively slow response times " +
	                      "and none to very few false clicks."
	                      )
	            fatigue_level = "Significant"
	        elif 2 < false_clicks <= 5:
	            rating = 2.5
	            comment = ("Your test results indicate that you have relatively slow response times " +
	                      "with a few number of false clicks."
	                      )
	            fatigue_level = "Significant"
	        else:
	            rating = 2
	            comment = ("Your test results indicate that you have relatively slow response times " +
	                      "with high number of false clicks."
	                      )
	            fatigue_level = "Significantly high"
	    
	    elif 700 < mean_rt <= 1000:
	        comment = ("Your test results indicate that you have significantly slow response times.")
	        
	        if false_clicks <= 2:
	            rating = 2
	            fatigue_level = "High"
	        else:
	            rating = 1.5
	            fatigue_level = "Excessive"
	            
	    elif 1000 < mean_rt:
	        comment = ("Your test results indicate that you have extremely slow response times."
	                  )
	        rating = 1
	        fatigue_level = "Excessive"
	        
	              
	    return (jsonify({"rating": rating, "comment": comment, "fatigue_level": fatigue_level}))
	            


	def chart_times(self):
		return response_time_chart(self.response_times, self.test_times)

            
            
            