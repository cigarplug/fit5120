import mysql.connector
from flask import jsonify
import os
import pandas as pd
import plotter
from tzinfo import melb_now


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
		self.kms = 5



	def crash_tod_atm(self):

		query = ("""
	    SELECT
	        sec_to_time(time_to_sec(a.accidentdate)- time_to_sec(a.accidentdate)%(30 * 60)) as tod,
	        ac.atmosph_cond_desc atm,
	        count(*) crashes
	    from
	    node n
	    left join accident a on
	        n.accident_no = a.accident_no
	    left join atmospheric_cond ac on
	        ac.accident_no = n.accident_no
	    where
	        ST_Distance_Sphere(Point(""" + str(self.lon) + ", " + str(self.lat) + "), n.coords) < " + str(self.kms*1000) + 
	    """
	    group by
	        tod,
	        atm
	    """)

		df = pd.read_sql_query(query, self.cnx)

		return plotter.tod_atm_stats(df)



	def crash_by_person(self):
    
	    query = ("""
	    select
	        p.sex,
	        p.age_group,
	        count(*) crashes    
	    from
	        node n   
	    left join person p on 
	    	p.accident_no  = n.accident_no
	    where
	        ST_Distance_Sphere(Point(""" + str(self.lon) + ", " + str(self.lat) + "), n.coords) < " + str(self.kms*1000) + 
	    """    
	    group by p.sex, p.age_group
	    """)
	    
	    df = pd.read_sql_query(query, self.cnx)

	    return plotter.age_sex_stats(df)


	def save_pvt(self, reaction_times, test_times):

		# get current date and time
	    now = melb_now()

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

