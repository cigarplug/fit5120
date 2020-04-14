import mysql.connector
from flask import jsonify
import os
import plotter
from datetime import datetime


class api:


	def __init__(self, lat = None, lon = None, age=None, sex=None):
		self.cnx = mysql.connector.connect(user=os.environ["user"],
								password=os.environ["password"],
								host=os.environ["host"],
								database=os.environ["database"])
		self.lat = lat
		self.lon = lon
		self.age = age
		self.sex = sex



	def get_crash_stats(self, kms = 3, min_count = 10):

		cursor = self.cnx.cursor()
		
		query = ("""

			select
				al.road_name,
				count(*) accident_count
			from
				node n
			left join accident_location al on
				n.accident_no = al.accident_no
			where
				ST_Distance_Sphere(Point(""" + str(self.lon) + ", " + str(self.lat) + "), n.coords) < " + str(kms*1000) + 
			"""
			GROUP by al.road_name 
			having accident_count >= """ + str(min_count)

			)

		cursor.execute(query)
		df = cursor.fetchall()

		cursor.close()

		return(jsonify(df))


	def crash_by_person(self, kms = 5):
    
	    query = ("""
	    select
	        p.sex,
	        p.age_group,
	        count(*) crashes    
	    from
	        node n   
	    left join person p
	    on p.accident_no  = n.accident_no
	    where
	        ST_Distance_Sphere(Point(""" + str(self.lon) + ", " + str(self.lat) + "), n.coords) < " + str(kms*1000) + 
	    """    
	    group by p.sex, p.age_group
	    """)
	    

	    return plotter.age_sex_stats(self.cnx, query)


	def save_pvt(self, reaction_times, test_times):

		# get current date and time
	    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	    # create database cursor object
	    cursor = self.cnx.cursor()

	    query = ("""
	    insert into pvt (`timestamp` , test_time , reaction_time ) values ('
	    """ + str(now) + """', '{"times":
	    """ + str(test_times) + """}', '{"times":
	    """ + str(reaction_times) + """}' )
	    """
	    )

	    #execute query and commit data
	    cursor.execute(query)
	    self.cnx.commit()

	    # close cursor object
	    cursor.close()

	    return(jsonify({"res": "OK"}))

	    

	def __del__(self):
		self.cnx.close()

